from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.carta.models import Categoria
from apps.usuarios.decorators import rol_requerido

from . import servicios
from .models import Mesa, Pedido

ACTIVOS = [Pedido.Estado.PENDIENTE, Pedido.Estado.EN_PREPARACION, Pedido.Estado.LISTO]


@rol_requerido('MESERO', 'ADMINISTRADOR')
def mesas(request):
    """Salón: estado de cada mesa (HU-10)."""
    lista = Mesa.objects.all()
    # Pedido activo de cada mesa ocupada (el último que no esté cancelado)
    activos = {
        p.mesa_id: p for p in Pedido.objects.filter(mesa__isnull=False).select_related('mesa')
        .exclude(estado=Pedido.Estado.CANCELADO).order_by('fecha_creacion')
        if p.mesa.estado == Mesa.Estado.OCUPADA
    }
    for m in lista:
        m.pedido_activo = activos.get(m.id)
    return render(request, 'pedidos/mesas.html', {'mesas': lista})


@rol_requerido('MESERO', 'CAJERO', 'ADMINISTRADOR')
def nuevo_pedido(request):
    """Tomar un pedido en tres pasos: mesa, platos y enviar (HU-11 a HU-13)."""
    categorias = Categoria.objects.prefetch_related('platos').order_by('nombre')
    mesas_libres = Mesa.objects.filter(estado=Mesa.Estado.LIBRE)

    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'MESA')
        items = []
        for categoria in categorias:
            for plato in categoria.platos.all():
                cantidad = request.POST.get(f'cantidad_{plato.id}', '0') or '0'
                if cantidad.isdigit() and int(cantidad) > 0:
                    items.append((plato, int(cantidad)))
        mesa, domicilio = None, None
        if tipo == 'DOMICILIO':
            domicilio = {
                'nombre_cliente': request.POST.get('nombre_cliente', '').strip(),
                'direccion': request.POST.get('direccion', '').strip(),
                'telefono': request.POST.get('telefono', '').strip(),
            }
            if not all(domicilio.values()):
                messages.error(request, 'Completa nombre, dirección y teléfono del domicilio.')
                return render(request, 'pedidos/nuevo.html', {
                    'categorias': categorias, 'mesas': mesas_libres, 'datos': request.POST})
        else:
            mesa = Mesa.objects.filter(pk=request.POST.get('mesa') or 0).first()
            if not mesa:
                messages.error(request, 'Elige una mesa.')
                return render(request, 'pedidos/nuevo.html', {
                    'categorias': categorias, 'mesas': mesas_libres, 'datos': request.POST})
        try:
            pedido = servicios.crear_pedido(
                request.user, items, mesa=mesa,
                observaciones=request.POST.get('observaciones', '').strip(), domicilio=domicilio,
            )
        except servicios.ErrorPedido as error:
            messages.error(request, str(error))
            return render(request, 'pedidos/nuevo.html', {
                'categorias': categorias, 'mesas': mesas_libres, 'datos': request.POST})
        messages.success(request, f'Pedido #{pedido.id} enviado a cocina ({pedido.destino}).')
        # El cajero toma domicilios por teléfono: vuelve a su lista de domicilios
        return redirect('domicilios' if request.user.rol == 'CAJERO' else 'mis_pedidos')

    return render(request, 'pedidos/nuevo.html', {
        'categorias': categorias, 'mesas': mesas_libres,
        'datos': {'mesa': request.GET.get('mesa', ''), 'tipo': request.GET.get('tipo', 'MESA')},
    })


@rol_requerido('MESERO', 'ADMINISTRADOR')
def mis_pedidos(request):
    """Pedidos de hoy. El mesero ve los suyos; el administrador ve todos."""
    inicio, fin = servicios.rango_de_hoy()
    pedidos = Pedido.objects.filter(fecha_creacion__gte=inicio, fecha_creacion__lt=fin) \
        .select_related('mesa', 'mesero').prefetch_related('detalles__plato')
    if request.user.rol == 'MESERO':
        pedidos = pedidos.filter(mesero=request.user)
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@rol_requerido('MESERO', 'ADMINISTRADOR')
@require_POST
def estado_pedido(request, pk):
    """El mesero marca un pedido como entregado o lo cancela."""
    pedido = get_object_or_404(Pedido, pk=pk)
    nuevo = request.POST.get('estado')
    if nuevo not in (Pedido.Estado.ENTREGADO, Pedido.Estado.CANCELADO):
        messages.error(request, 'Acción no permitida.')
    else:
        try:
            servicios.cambiar_estado(pedido, nuevo)
            messages.success(request, f'Pedido #{pedido.id}: {Pedido.Estado(nuevo).label.lower()}.')
        except servicios.ErrorPedido as error:
            messages.error(request, str(error))
    return redirect('mis_pedidos')


@rol_requerido('COCINA', 'ADMINISTRADOR')
def cocina(request):
    """Tablero de cocina. Los datos llegan por la API con JavaScript (ver cocina.js)."""
    return render(request, 'pedidos/cocina.html')

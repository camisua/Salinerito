from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.pedidos.models import Pedido
from apps.pedidos.servicios import rango_de_hoy
from apps.usuarios.decorators import rol_requerido

from . import servicios
from .models import CierreCaja, Factura, MetodoPago

ROLES_CAJA = ('CAJERO', 'ADMINISTRADOR')


@rol_requerido(*ROLES_CAJA)
def por_cobrar(request):
    """Pedidos entregados pendientes de pago."""
    return render(request, 'caja/por_cobrar.html', {'pedidos': servicios.pedidos_por_cobrar()})


@rol_requerido(*ROLES_CAJA)
def cobrar(request, pk):
    """Detalle del pedido, método de pago y generación de la factura (HU-19)."""
    pedido = get_object_or_404(Pedido.objects.prefetch_related('detalles__plato'), pk=pk)
    if request.method == 'POST':
        try:
            factura = servicios.facturar(pedido, request.user, request.POST.get('metodo_pago'))
        except servicios.ErrorCaja as error:
            messages.error(request, str(error))
            return redirect('por_cobrar')
        messages.success(request, f'Factura {factura.numero} generada.')
        return redirect('ver_factura', factura.pk)
    return render(request, 'caja/cobrar.html', {'pedido': pedido, 'metodos': MetodoPago.choices})


@rol_requerido(*ROLES_CAJA)
def ver_factura(request, pk):
    """Factura lista para imprimir."""
    factura = get_object_or_404(
        Factura.objects.select_related('pedido__mesa', 'pedido__domicilio', 'cajero'), pk=pk)
    return render(request, 'caja/factura.html', {'factura': factura})


@rol_requerido(*ROLES_CAJA)
def domicilios(request):
    """Domicilios de hoy con su estado."""
    inicio, fin = rango_de_hoy()
    lista = Pedido.objects.filter(tipo=Pedido.Tipo.DOMICILIO, fecha_creacion__gte=inicio, fecha_creacion__lt=fin) \
        .select_related('domicilio').prefetch_related('detalles__plato')
    return render(request, 'caja/domicilios.html', {'pedidos': lista})


@rol_requerido(*ROLES_CAJA)
def cierre(request):
    """Cierre de caja del turno (HU-20, RF-10)."""
    if request.method == 'POST':
        try:
            nuevo = servicios.cerrar_caja(request.user)
            messages.success(request, f'Cierre #{nuevo.id} realizado: {nuevo.numero_pedidos} facturas.')
        except servicios.ErrorCaja as error:
            messages.error(request, str(error))
        return redirect('cierre_caja')
    return render(request, 'caja/cierre.html', {
        'resumen': servicios.resumen_pendiente(),
        'cierres': CierreCaja.objects.select_related('cajero')[:10],
    })

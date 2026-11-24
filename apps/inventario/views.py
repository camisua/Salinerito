from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.decorators import rol_requerido

from .forms import CompraInsumoForm, InsumoForm
from .models import CompraInsumo, Insumo


@rol_requerido('ADMINISTRADOR')
def lista_insumos(request):
    """Existencias con alertas y formulario para registrar una compra (HU-07, HU-08)."""
    form_compra = CompraInsumoForm(request.POST or None)
    if request.method == 'POST' and form_compra.is_valid():
        compra = form_compra.save()  # al guardar, suma a la existencia (ver models.py)
        messages.success(request, f'Compra registrada: {compra.cantidad} {compra.insumo.unidad} de {compra.insumo.nombre}.')
        return redirect('lista_insumos')

    insumos = Insumo.objects.all()
    return render(request, 'inventario/lista.html', {
        'insumos': insumos,
        'alertas': [i for i in insumos if i.bajo_minimo],
        'form_compra': form_compra,
        'ultimas_compras': CompraInsumo.objects.select_related('insumo')[:5],
    })


@rol_requerido('ADMINISTRADOR')
def editar_insumo(request, pk=None):
    """Crear (pk vacío) o editar un insumo."""
    insumo = get_object_or_404(Insumo, pk=pk) if pk else None
    form = InsumoForm(request.POST or None, instance=insumo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Insumo guardado.')
        return redirect('lista_insumos')
    return render(request, 'inventario/form.html', {'form': form, 'insumo': insumo})

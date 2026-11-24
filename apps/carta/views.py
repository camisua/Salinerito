from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.usuarios.decorators import rol_requerido

from .forms import PlatoForm, RecetaFormSet
from .models import Categoria, Plato


@rol_requerido('ADMINISTRADOR')
def lista_platos(request):
    """Carta con filtro por categoría (HU-09)."""
    platos = Plato.objects.select_related('categoria').prefetch_related('recetas__insumo')
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        platos = platos.filter(categoria_id=categoria_id)
    return render(request, 'carta/lista.html', {
        'platos': platos,
        'categorias': Categoria.objects.all(),
        'categoria_id': categoria_id,
    })


@rol_requerido('ADMINISTRADOR')
def editar_plato(request, pk=None):
    """Crear o editar un plato junto con su receta."""
    plato = get_object_or_404(Plato, pk=pk) if pk else Plato()
    form = PlatoForm(request.POST or None, instance=plato)
    receta = RecetaFormSet(request.POST or None, instance=plato)
    if request.method == 'POST' and form.is_valid() and receta.is_valid():
        # transaction.atomic: se guarda el plato y su receta, o nada.
        with transaction.atomic():
            plato = form.save()
            receta.instance = plato
            receta.save()
        messages.success(request, f'Plato "{plato.nombre}" guardado.')
        return redirect('lista_platos')
    return render(request, 'carta/form.html', {'form': form, 'receta': receta, 'plato': plato})


@rol_requerido('ADMINISTRADOR')
@require_POST
def cambiar_estado_plato(request, pk):
    """Activa o desactiva un plato. Los platos no se borran."""
    plato = get_object_or_404(Plato, pk=pk)
    plato.activo = not plato.activo
    plato.save(update_fields=['activo'])
    estado = 'activado' if plato.activo else 'desactivado'
    messages.info(request, f'"{plato.nombre}" {estado}.')
    return redirect('lista_platos')

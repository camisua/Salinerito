"""Reglas del negocio de los pedidos.

Las vistas (pantallas) y la API llaman estas funciones, así la lógica
está en un solo lugar y no se repite.
"""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.utils import timezone

from apps.inventario.models import Insumo

from .models import DetallePedido, Domicilio, Mesa, Pedido


def rango_de_hoy():
    """Inicio y fin del día de hoy en la hora de Colombia.

    Se usa en lugar de fecha_creacion__date porque MySQL en Windows no trae
    las tablas de zonas horarias y ese filtro no encuentra nada.
    """
    inicio = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio, inicio + timedelta(days=1)


class ErrorPedido(Exception):
    """Error de negocio con un mensaje para mostrarle al usuario."""


# Qué cambios de estado están permitidos y qué hora se guarda en cada uno
TRANSICIONES = {
    Pedido.Estado.PENDIENTE: [Pedido.Estado.EN_PREPARACION, Pedido.Estado.CANCELADO],
    Pedido.Estado.EN_PREPARACION: [Pedido.Estado.LISTO],
    Pedido.Estado.LISTO: [Pedido.Estado.ENTREGADO],
}
CAMPO_HORA = {
    Pedido.Estado.EN_PREPARACION: 'hora_preparacion',
    Pedido.Estado.LISTO: 'hora_listo',
    Pedido.Estado.ENTREGADO: 'hora_entrega',
}


def _verificar_existencias(items):
    """Revisa que haya insumos suficientes para todos los platos pedidos."""
    necesario = defaultdict(Decimal)
    for plato, cantidad in items:
        for receta in plato.recetas.select_related('insumo'):
            necesario[receta.insumo] += receta.cantidad * cantidad
    faltantes = [i.nombre for i, cant in necesario.items() if i.existencia < cant]
    if faltantes:
        raise ErrorPedido('No hay suficiente: ' + ', '.join(faltantes) + '.')


@transaction.atomic
def crear_pedido(mesero, items, mesa=None, observaciones='', domicilio=None):
    """Crea el pedido con sus platos (HU-11 a HU-13).

    items: lista de (plato, cantidad).
    mesa: la mesa, o None si es domicilio.
    domicilio: diccionario con nombre_cliente, direccion y telefono.
    """
    items = [(p, c) for p, c in items if c > 0]
    if not items:
        raise ErrorPedido('Agrega al menos un plato.')
    if any(not p.activo for p, _ in items):
        raise ErrorPedido('Hay platos inactivos en el pedido.')
    if mesa is None and not domicilio:
        raise ErrorPedido('Elige una mesa o ingresa los datos del domicilio.')
    if mesa is not None:
        mesa = Mesa.objects.select_for_update().get(pk=mesa.pk)  # bloquea la mesa mientras se crea
        if mesa.estado != Mesa.Estado.LIBRE:
            raise ErrorPedido(f'La {mesa} ya está ocupada.')
    _verificar_existencias(items)

    pedido = Pedido.objects.create(
        mesero=mesero,
        mesa=mesa,
        tipo=Pedido.Tipo.MESA if mesa else Pedido.Tipo.DOMICILIO,
        observaciones=observaciones,
    )
    for plato, cantidad in items:
        DetallePedido.objects.create(
            pedido=pedido, plato=plato, cantidad=cantidad,
            precio_unitario=plato.precio,  # se guarda el precio de hoy (histórico)
        )
    if domicilio:
        Domicilio.objects.create(pedido=pedido, **domicilio)
    if mesa:
        mesa.ocupar()
    return pedido


@transaction.atomic
def editar_pedido(pedido, items, observaciones=''):
    """Cambia los platos de un pedido que la cocina aún no empieza (HU-14)."""
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.estado != Pedido.Estado.PENDIENTE:
        raise ErrorPedido('Solo se puede editar un pedido pendiente: la cocina ya lo empezó.')
    items = [(p, c) for p, c in items if c > 0]
    if not items:
        raise ErrorPedido('Agrega al menos un plato. Si el cliente ya no quiere nada, cancela el pedido.')
    _verificar_existencias(items)
    pedido.detalles.all().delete()
    for plato, cantidad in items:
        DetallePedido.objects.create(pedido=pedido, plato=plato, cantidad=cantidad, precio_unitario=plato.precio)
    pedido.observaciones = observaciones
    pedido.save(update_fields=['observaciones'])
    return pedido


@transaction.atomic
def cambiar_estado(pedido, nuevo):
    """Mueve el pedido al siguiente estado y guarda la hora (HU-15 a HU-17)."""
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if nuevo not in TRANSICIONES.get(pedido.estado, []):
        raise ErrorPedido(
            f'No se puede pasar de {pedido.get_estado_display()} a {Pedido.Estado(nuevo).label}.'
        )
    pedido.estado = nuevo
    campos = ['estado']
    if nuevo in CAMPO_HORA:
        setattr(pedido, CAMPO_HORA[nuevo], timezone.now())
        campos.append(CAMPO_HORA[nuevo])
    pedido.save(update_fields=campos)

    if nuevo == Pedido.Estado.ENTREGADO:
        descontar_inventario(pedido)
    if nuevo == Pedido.Estado.CANCELADO and pedido.mesa:
        pedido.mesa.liberar()
    return pedido


def descontar_inventario(pedido):
    """RF-07: al entregar, resta de cada insumo lo que dice la receta × cantidad."""
    for detalle in pedido.detalles.prefetch_related('plato__recetas'):
        for receta in detalle.plato.recetas.all():
            gasto = receta.cantidad * detalle.cantidad
            # Greatest(..., 0) evita que la existencia quede negativa
            Insumo.objects.filter(pk=receta.insumo_id).update(
                existencia=Greatest(F('existencia') - gasto, Decimal('0'))
            )

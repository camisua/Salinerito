"""Reglas del negocio de la caja."""
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum

from apps.pedidos.models import Pedido

from .models import CierreCaja, Factura, MetodoPago


class ErrorCaja(Exception):
    """Error de negocio con un mensaje para el usuario."""


def pedidos_por_cobrar():
    """Pedidos entregados que aún no tienen factura."""
    return Pedido.objects.filter(estado=Pedido.Estado.ENTREGADO, factura__isnull=True) \
        .select_related('mesa', 'mesero', 'domicilio').prefetch_related('detalles__plato') \
        .order_by('hora_entrega')


@transaction.atomic
def facturar(pedido, cajero, metodo_pago):
    """Genera la factura, registra el pago y libera la mesa."""
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.estado != Pedido.Estado.ENTREGADO:
        raise ErrorCaja('Solo se cobran pedidos entregados.')
    if Factura.objects.filter(pedido=pedido).exists():
        raise ErrorCaja('Este pedido ya fue cobrado.')
    if metodo_pago not in MetodoPago.values:
        raise ErrorCaja('Método de pago no válido.')

    factura = Factura.objects.create(
        pedido=pedido, cajero=cajero, metodo_pago=metodo_pago, total=pedido.calcular_total(),
    )
    # El número se arma con el id: FV-000001, FV-000002...
    factura.numero = f'FV-{factura.id:06d}'
    factura.save(update_fields=['numero'])

    if pedido.mesa:
        pedido.mesa.liberar()
    return factura


def resumen_pendiente():
    """Totales por método de las facturas que aún no entran en un cierre."""
    facturas = Factura.objects.filter(cierre__isnull=True)
    por_metodo = {fila['metodo_pago']: fila['suma'] for fila in
                  facturas.values('metodo_pago').annotate(suma=Sum('total'))}
    efectivo = por_metodo.get(MetodoPago.EFECTIVO, Decimal('0'))
    tarjeta = por_metodo.get(MetodoPago.TARJETA, Decimal('0'))
    transferencia = por_metodo.get(MetodoPago.TRANSFERENCIA, Decimal('0'))
    return {
        'facturas': facturas.select_related('pedido__mesa'),
        'efectivo': efectivo,
        'tarjeta': tarjeta,
        'transferencia': transferencia,
        'total': efectivo + tarjeta + transferencia,
        'cantidad': facturas.aggregate(n=Count('id'))['n'],
    }


@transaction.atomic
def cerrar_caja(cajero):
    """Crea el cierre con los totales y marca las facturas como cerradas."""
    resumen = resumen_pendiente()
    if resumen['cantidad'] == 0:
        raise ErrorCaja('No hay facturas nuevas para cerrar.')
    cierre = CierreCaja.objects.create(
        cajero=cajero,
        total_efectivo=resumen['efectivo'],
        total_tarjeta=resumen['tarjeta'],
        total_transferencia=resumen['transferencia'],
        total_general=resumen['total'],
        numero_pedidos=resumen['cantidad'],
    )
    Factura.objects.filter(cierre__isnull=True).update(cierre=cierre)
    return cierre

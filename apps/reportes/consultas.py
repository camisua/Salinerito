"""Consultas para el panel y los reportes (RF-11).

Ojo: no usamos filtros como fecha__date ni TruncDate, porque MySQL en
Windows no tiene las tablas de zonas horarias. Filtramos por rangos de
hora y agrupamos por día en Python.
"""
from collections import OrderedDict
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone

from apps.caja.models import Factura, MetodoPago
from apps.inventario.models import Insumo
from apps.pedidos.models import DetallePedido, Mesa, Pedido


def rango(desde, hasta):
    """Convierte dos fechas (date) en un rango de horas de Colombia [desde 00:00, hasta+1 00:00)."""
    zona = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(desde, time.min), zona)
    fin = timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min), zona)
    return inicio, fin


def resumen_del_dia():
    """Números del panel del administrador."""
    hoy = timezone.localdate()
    inicio, fin = rango(hoy, hoy)
    facturas_hoy = Factura.objects.filter(fecha__gte=inicio, fecha__lt=fin)
    return {
        'ventas_hoy': facturas_hoy.aggregate(t=Sum('total'))['t'] or Decimal('0'),
        'facturas_hoy': facturas_hoy.count(),
        'pedidos_activos': Pedido.objects.filter(
            estado__in=[Pedido.Estado.PENDIENTE, Pedido.Estado.EN_PREPARACION, Pedido.Estado.LISTO]).count(),
        'mesas_ocupadas': Mesa.objects.filter(estado=Mesa.Estado.OCUPADA).count(),
        'mesas_total': Mesa.objects.count(),
        'alertas': list(Insumo.objects.filter(existencia__lte=F('cantidad_minima'))),
        'ultimos_pedidos': Pedido.objects.select_related('mesa', 'mesero')
            .prefetch_related('detalles').filter(fecha_creacion__gte=inicio, fecha_creacion__lt=fin)[:8],
    }


def ventas_por_dia(desde, hasta):
    """Total vendido cada día del rango (incluye los días en cero)."""
    inicio, fin = rango(desde, hasta)
    dias = OrderedDict()
    dia = desde
    while dia <= hasta:
        dias[dia] = Decimal('0')
        dia += timedelta(days=1)
    for factura in Factura.objects.filter(fecha__gte=inicio, fecha__lt=fin).only('fecha', 'total'):
        dias[timezone.localtime(factura.fecha).date()] += factura.total
    maximo = max(dias.values(), default=0) or 1
    return [{'dia': d, 'total': t, 'porcentaje': int(t * 100 / maximo)} for d, t in dias.items()]


def ventas_por_metodo(desde, hasta):
    inicio, fin = rango(desde, hasta)
    totales = dict(Factura.objects.filter(fecha__gte=inicio, fecha__lt=fin)
                   .values_list('metodo_pago').annotate(t=Sum('total')))
    return [{'metodo': texto, 'total': totales.get(valor, Decimal('0'))} for valor, texto in MetodoPago.choices]


def platos_mas_vendidos(desde, hasta, limite=10):
    """Platos cobrados en el rango, ordenados por cantidad."""
    inicio, fin = rango(desde, hasta)
    subtotal = ExpressionWrapper(F('cantidad') * F('precio_unitario'),
                                 output_field=DecimalField(max_digits=12, decimal_places=2))
    return list(
        DetallePedido.objects.filter(pedido__factura__fecha__gte=inicio, pedido__factura__fecha__lt=fin)
        .values('plato__nombre')
        .annotate(cantidad_total=Sum('cantidad'), vendido=Sum(subtotal))
        .order_by('-cantidad_total')[:limite]
    )


def tiempo_promedio_cocina(desde, hasta):
    """Minutos promedio entre 'Empezar' y 'Listo' (RF-06)."""
    inicio, fin = rango(desde, hasta)
    pedidos = Pedido.objects.filter(hora_listo__gte=inicio, hora_listo__lt=fin,
                                    hora_preparacion__isnull=False).only('hora_preparacion', 'hora_listo')
    tiempos = [(p.hora_listo - p.hora_preparacion).total_seconds() / 60 for p in pedidos]
    return round(sum(tiempos) / len(tiempos), 1) if tiempos else None


def facturas(desde, hasta):
    inicio, fin = rango(desde, hasta)
    return Factura.objects.filter(fecha__gte=inicio, fecha__lt=fin) \
        .select_related('pedido__mesa', 'cajero').order_by('fecha')

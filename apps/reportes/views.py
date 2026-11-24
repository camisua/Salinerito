import csv
from datetime import date, timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.usuarios.decorators import rol_requerido

from . import consultas


def _fechas(request):
    """Lee ?desde=AAAA-MM-DD&hasta=AAAA-MM-DD. Por defecto: los últimos 7 días."""
    hoy = timezone.localdate()
    try:
        hasta = date.fromisoformat(request.GET.get('hasta', ''))
    except ValueError:
        hasta = hoy
    try:
        desde = date.fromisoformat(request.GET.get('desde', ''))
    except ValueError:
        desde = hasta - timedelta(days=6)
    if desde > hasta:
        desde, hasta = hasta, desde
    return desde, hasta


@rol_requerido('ADMINISTRADOR')
def panel(request):
    """Panel del administrador: resumen del turno (HU-18, HU-21)."""
    return render(request, 'reportes/panel.html', consultas.resumen_del_dia())


@rol_requerido('ADMINISTRADOR')
def reportes(request):
    """Reportes de ventas por rango de fechas (HU-22, RF-11)."""
    desde, hasta = _fechas(request)
    por_dia = consultas.ventas_por_dia(desde, hasta)
    return render(request, 'reportes/reportes.html', {
        'desde': desde, 'hasta': hasta,
        'por_dia': por_dia,
        'total': sum(d['total'] for d in por_dia),
        'por_metodo': consultas.ventas_por_metodo(desde, hasta),
        'platos': consultas.platos_mas_vendidos(desde, hasta),
        'tiempo_cocina': consultas.tiempo_promedio_cocina(desde, hasta),
        'num_facturas': consultas.facturas(desde, hasta).count(),
    })


@rol_requerido('ADMINISTRADOR')
def exportar_csv(request):
    """Descarga las facturas del rango en un archivo CSV que abre Excel."""
    desde, hasta = _fechas(request)
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="ventas_{desde}_{hasta}.csv"'
    respuesta.write('﻿')  # para que Excel muestre bien las tildes
    escritor = csv.writer(respuesta, delimiter=';')
    escritor.writerow(['Factura', 'Fecha', 'Pedido', 'Destino', 'Método de pago', 'Cajero', 'Total'])
    for f in consultas.facturas(desde, hasta):
        escritor.writerow([
            f.numero, timezone.localtime(f.fecha).strftime('%d/%m/%Y %H:%M'), f.pedido_id,
            f.pedido.destino, f.get_metodo_pago_display(),
            f.cajero.get_full_name() or f.cajero.username, int(f.total),
        ])
    return respuesta

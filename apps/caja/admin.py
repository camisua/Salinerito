from django.contrib import admin

from .models import CierreCaja, Factura


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'pedido', 'total', 'metodo_pago', 'cajero', 'fecha', 'cierre')
    list_filter = ('metodo_pago',)


@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'cajero', 'total_efectivo', 'total_tarjeta', 'total_transferencia',
                    'total_general', 'numero_pedidos')

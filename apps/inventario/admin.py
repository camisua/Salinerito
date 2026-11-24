from django.contrib import admin
from django.utils.html import format_html

from .models import CompraInsumo, Insumo


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad', 'existencia', 'cantidad_minima', 'alerta')
    search_fields = ('nombre',)

    @admin.display(description='estado')
    def alerta(self, obj):
        # Muestra en rojo los insumos que hay que comprar
        if obj.bajo_minimo:
            return format_html('<b style="color:#B03A2E">{}</b>', 'Comprar')
        return format_html('<span style="color:#2E7D4F">{}</span>', 'OK')


@admin.register(CompraInsumo)
class CompraInsumoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'insumo', 'cantidad', 'costo')
    list_filter = ('fecha', 'insumo')
    date_hierarchy = 'fecha'

    def get_readonly_fields(self, request, obj=None):
        # Una compra ya registrada no se edita: ya sumó al inventario.
        if obj:
            return ('insumo', 'fecha', 'cantidad', 'costo')
        return ()

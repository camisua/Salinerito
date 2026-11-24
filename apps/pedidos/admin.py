from django.contrib import admin

from .models import DetallePedido, Domicilio, Mesa, Pedido


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidad', 'estado')
    list_filter = ('estado',)


class DetalleInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


class DomicilioInline(admin.StackedInline):
    model = Domicilio
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'mesa', 'mesero', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'tipo')
    inlines = [DetalleInline, DomicilioInline]

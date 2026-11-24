from django.contrib import admin

from .models import Categoria, Plato, Receta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


class RecetaInline(admin.TabularInline):
    """Permite escribir la receta dentro de la misma pantalla del plato."""
    model = Receta
    extra = 1
    autocomplete_fields = ('insumo',)


@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'activo')
    list_filter = ('categoria', 'activo')
    list_editable = ('activo',)
    search_fields = ('nombre',)
    inlines = [RecetaInline]

    def has_delete_permission(self, request, obj=None):
        # Los platos no se borran (ya pueden estar en pedidos): se desactivan.
        return False

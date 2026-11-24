from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Pantalla del panel /admin para que el administrador cree y edite cuentas."""

    list_display = ('username', 'first_name', 'last_name', 'email', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol en el restaurante', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del empleado', {'fields': ('first_name', 'last_name', 'email', 'rol')}),
    )

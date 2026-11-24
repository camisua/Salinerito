from rest_framework.permissions import BasePermission


class RolPermitido(BasePermission):
    """Igual que @rol_requerido, pero para la API.

    Cada vista de la API dice qué roles la pueden usar con: roles = [...]
    """

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario.is_authenticated:
            return False
        return usuario.is_superuser or usuario.rol in getattr(view, 'roles', [])

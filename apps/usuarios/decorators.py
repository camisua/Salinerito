from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def rol_requerido(*roles):
    """Permite entrar a una vista solo a los roles indicados.

    Uso:
        @rol_requerido('ADMINISTRADOR')
        def mi_vista(request): ...

    Si no ha iniciado sesión, lo manda al login.
    Si su rol no está permitido, muestra la página 403 (acceso denegado).
    """
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if request.user.is_superuser or request.user.rol in roles:
                return vista(request, *args, **kwargs)
            raise PermissionDenied
        return envoltura
    return decorador

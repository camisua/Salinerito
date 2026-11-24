from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def inicio(request):
    """Página de inicio. El administrador va directo a su panel con el resumen del día."""
    if request.user.rol == 'ADMINISTRADOR' or request.user.is_superuser:
        return redirect('panel')
    return render(request, 'inicio.html')

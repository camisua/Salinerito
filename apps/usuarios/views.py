from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inicio(request):
    """Página de bienvenida: muestra los módulos que puede usar el rol del empleado."""
    return render(request, 'inicio.html')

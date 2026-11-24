from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CambiarContrasenaForm, MisDatosForm


@login_required
def inicio(request):
    """Página de inicio. El administrador va directo a su panel con el resumen del día."""
    if request.user.rol == 'ADMINISTRADOR' or request.user.is_superuser:
        return redirect('panel')
    return render(request, 'inicio.html')


@login_required
def mi_cuenta(request):
    """Cada empleado edita sus datos y cambia su contraseña (HU-03)."""
    form_datos = MisDatosForm(instance=request.user)
    form_clave = CambiarContrasenaForm(request.user)
    if request.method == 'POST' and 'guardar_datos' in request.POST:
        form_datos = MisDatosForm(request.POST, instance=request.user)
        if form_datos.is_valid():
            form_datos.save()
            messages.success(request, 'Tus datos se actualizaron.')
            return redirect('mi_cuenta')
    elif request.method == 'POST' and 'cambiar_clave' in request.POST:
        form_clave = CambiarContrasenaForm(request.user, request.POST)
        if form_clave.is_valid():
            usuario = form_clave.save()
            update_session_auth_hash(request, usuario)  # para no cerrar la sesión
            messages.success(request, 'Tu contraseña se cambió.')
            return redirect('mi_cuenta')
    return render(request, 'usuarios/mi_cuenta.html', {'form_datos': form_datos, 'form_clave': form_clave})

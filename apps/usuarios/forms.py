from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import Usuario


class EstiloBootstrapMixin:
    """Agrega las clases de Bootstrap a todos los campos de un formulario.

    Así no hay que escribir class="form-control" campo por campo en el HTML.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select'
            else:
                widget.attrs['class'] = 'form-control'


class MisDatosForm(EstiloBootstrapMixin, forms.ModelForm):
    """El empleado actualiza su nombre y correo (HU-03)."""

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']


class CambiarContrasenaForm(EstiloBootstrapMixin, PasswordChangeForm):
    """Formulario de Django para cambiar la contraseña, con estilo Bootstrap (HU-03)."""

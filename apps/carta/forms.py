from django import forms

from apps.usuarios.forms import EstiloBootstrapMixin

from .models import Plato, Receta


class PlatoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'activo']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 2})}


class RecetaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['insumo', 'cantidad']


# Un "formset" es un grupo de formularios iguales: una fila por ingrediente.
RecetaFormSet = forms.inlineformset_factory(
    Plato, Receta, form=RecetaForm, extra=2, can_delete=True,
)

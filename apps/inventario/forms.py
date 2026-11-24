from django import forms

from apps.usuarios.forms import EstiloBootstrapMixin

from .models import CompraInsumo, Insumo


class InsumoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre', 'unidad', 'existencia', 'cantidad_minima']


class CompraInsumoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = CompraInsumo
        fields = ['insumo', 'fecha', 'cantidad', 'costo']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

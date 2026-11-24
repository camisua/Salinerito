from django import forms


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

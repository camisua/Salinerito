from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.utils import timezone


class Insumo(models.Model):
    """Ingrediente o producto que se gasta al preparar los platos."""

    nombre = models.CharField('nombre', max_length=100, unique=True)
    unidad = models.CharField('unidad', max_length=20, help_text='kg, litro, unidad...')
    existencia = models.DecimalField(
        'existencia', max_digits=10, decimal_places=3, default=0,
        validators=[MinValueValidator(0)],
    )
    cantidad_minima = models.DecimalField(
        'cantidad mínima', max_digits=10, decimal_places=3, default=0,
        validators=[MinValueValidator(0)],
        help_text='Si la existencia llega a este valor, el sistema muestra una alerta.',
    )

    class Meta:
        db_table = 'insumo'
        ordering = ['nombre']
        verbose_name = 'insumo'
        verbose_name_plural = 'insumos'

    def __str__(self):
        return f'{self.nombre} ({self.unidad})'

    @property
    def bajo_minimo(self):
        """True cuando hay que comprar más (alerta de RF-08)."""
        return self.existencia <= self.cantidad_minima


class CompraInsumo(models.Model):
    """Compra de un insumo. Al registrarla, aumenta la existencia."""

    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name='compras')
    fecha = models.DateField('fecha', default=timezone.localdate)
    cantidad = models.DecimalField(
        'cantidad', max_digits=10, decimal_places=3,
        validators=[MinValueValidator(0.001)],
    )
    costo = models.DecimalField(
        'costo total', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        db_table = 'compra_insumo'
        ordering = ['-fecha', '-id']
        verbose_name = 'compra de insumo'
        verbose_name_plural = 'compras de insumos'

    def __str__(self):
        return f'{self.fecha} · {self.insumo.nombre} · {self.cantidad} {self.insumo.unidad}'

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        super().save(*args, **kwargs)
        if es_nueva:
            # Regla del negocio: cada compra nueva suma al inventario.
            # F() hace la suma directamente en MySQL, así no se pierde
            # ninguna compra si dos personas registran al mismo tiempo.
            Insumo.objects.filter(pk=self.insumo_id).update(
                existencia=F('existencia') + self.cantidad
            )

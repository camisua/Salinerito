from django.core.validators import MinValueValidator
from django.db import models

from apps.inventario.models import Insumo


class Categoria(models.Model):
    """Grupo de la carta: sopas, platos fuertes, bebidas..."""

    nombre = models.CharField('nombre', max_length=60, unique=True)

    class Meta:
        db_table = 'categoria'
        ordering = ['nombre']
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    """Plato o bebida que se vende. No se borra: se desactiva."""

    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='platos', verbose_name='categoría',
    )
    nombre = models.CharField('nombre', max_length=100, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    precio = models.DecimalField(
        'precio', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    activo = models.BooleanField('activo', default=True)
    insumos = models.ManyToManyField(Insumo, through='Receta', related_name='platos')

    class Meta:
        db_table = 'plato'
        ordering = ['categoria__nombre', 'nombre']
        verbose_name = 'plato'
        verbose_name_plural = 'platos'

    def __str__(self):
        return self.nombre

    def esta_disponible(self):
        """True si hay insumos suficientes para preparar una porción."""
        return all(r.insumo.existencia >= r.cantidad for r in self.recetas.select_related('insumo'))


class Receta(models.Model):
    """Cuánto de cada insumo gasta una porción del plato (tabla intermedia N:M)."""

    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='recetas')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name='recetas', verbose_name='insumo')
    cantidad = models.DecimalField(
        'cantidad por porción', max_digits=10, decimal_places=3,
        validators=[MinValueValidator(0.001)],
    )

    class Meta:
        db_table = 'receta'
        verbose_name = 'ingrediente de la receta'
        verbose_name_plural = 'receta'
        constraints = [
            models.UniqueConstraint(fields=['plato', 'insumo'], name='uq_receta'),
        ]

    def __str__(self):
        return f'{self.plato.nombre}: {self.cantidad} {self.insumo.unidad} de {self.insumo.nombre}'

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.carta.models import Plato


class Mesa(models.Model):
    """Mesa del salón."""

    class Estado(models.TextChoices):
        LIBRE = 'LIBRE', 'Libre'
        OCUPADA = 'OCUPADA', 'Ocupada'

    numero = models.PositiveIntegerField('número', unique=True)
    capacidad = models.PositiveIntegerField('capacidad', default=4)
    estado = models.CharField('estado', max_length=10, choices=Estado.choices, default=Estado.LIBRE)

    class Meta:
        db_table = 'mesa'
        ordering = ['numero']
        verbose_name = 'mesa'
        verbose_name_plural = 'mesas'

    def __str__(self):
        return f'Mesa {self.numero}'

    def ocupar(self):
        self.estado = self.Estado.OCUPADA
        self.save(update_fields=['estado'])

    def liberar(self):
        self.estado = self.Estado.LIBRE
        self.save(update_fields=['estado'])


class Pedido(models.Model):
    """Pedido de una mesa o a domicilio."""

    class Tipo(models.TextChoices):
        MESA = 'MESA', 'Mesa'
        DOMICILIO = 'DOMICILIO', 'Domicilio'

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PREPARACION = 'EN_PREPARACION', 'En preparación'
        LISTO = 'LISTO', 'Listo'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    tipo = models.CharField('tipo', max_length=10, choices=Tipo.choices, default=Tipo.MESA)
    estado = models.CharField('estado', max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, null=True, blank=True, related_name='pedidos')
    mesero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    observaciones = models.CharField('observaciones', max_length=255, blank=True)
    fecha_creacion = models.DateTimeField('creado', auto_now_add=True)
    hora_preparacion = models.DateTimeField('inicio de preparación', null=True, blank=True)
    hora_listo = models.DateTimeField('listo', null=True, blank=True)
    hora_entrega = models.DateTimeField('entregado', null=True, blank=True)

    class Meta:
        db_table = 'pedido'
        ordering = ['-fecha_creacion']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido #{self.id} · {self.destino}'

    @property
    def destino(self):
        return str(self.mesa) if self.mesa else 'Domicilio'

    def calcular_total(self):
        return sum((d.subtotal for d in self.detalles.all()), Decimal('0'))


class DetallePedido(models.Model):
    """Cada plato del pedido con su cantidad. Guarda el precio del momento."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT, related_name='detalles')
    cantidad = models.PositiveIntegerField('cantidad', validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('precio unitario', max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = 'detalle del pedido'
        verbose_name_plural = 'detalles del pedido'

    def __str__(self):
        return f'{self.cantidad} × {self.plato.nombre}'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Domicilio(models.Model):
    """Datos de entrega de un pedido a domicilio (relación 1 a 1 con Pedido)."""

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='domicilio')
    nombre_cliente = models.CharField('cliente', max_length=100)
    direccion = models.CharField('dirección', max_length=200)
    telefono = models.CharField('teléfono', max_length=20)

    class Meta:
        db_table = 'domicilio'
        verbose_name = 'domicilio'
        verbose_name_plural = 'domicilios'

    def __str__(self):
        return f'{self.nombre_cliente} · {self.direccion}'

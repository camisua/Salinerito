from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.pedidos.models import Pedido


class MetodoPago(models.TextChoices):
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TARJETA = 'TARJETA', 'Tarjeta'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'


class CierreCaja(models.Model):
    """Resumen del turno: totales por método de pago (HU-20, RF-10)."""

    cajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cierres')
    fecha = models.DateField('fecha', default=timezone.localdate)
    hora = models.DateTimeField('hora del cierre', auto_now_add=True)
    total_efectivo = models.DecimalField('efectivo', max_digits=12, decimal_places=2, default=0)
    total_tarjeta = models.DecimalField('tarjeta', max_digits=12, decimal_places=2, default=0)
    total_transferencia = models.DecimalField('transferencia', max_digits=12, decimal_places=2, default=0)
    total_general = models.DecimalField('total', max_digits=12, decimal_places=2, default=0)
    numero_pedidos = models.PositiveIntegerField('pedidos', default=0)

    class Meta:
        db_table = 'cierre_caja'
        ordering = ['-hora']
        verbose_name = 'cierre de caja'
        verbose_name_plural = 'cierres de caja'

    def __str__(self):
        return f'Cierre #{self.id} · {self.fecha}'


class Factura(models.Model):
    """Cobro de un pedido entregado (HU-19, RF-09). Relación 1 a 1 con Pedido."""

    numero = models.CharField('número', max_length=20, unique=True, blank=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name='factura')
    cajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='facturas')
    cierre = models.ForeignKey(CierreCaja, on_delete=models.PROTECT, null=True, blank=True, related_name='facturas')
    fecha = models.DateTimeField('fecha', auto_now_add=True)
    total = models.DecimalField('total', max_digits=12, decimal_places=2)
    metodo_pago = models.CharField('método de pago', max_length=15, choices=MetodoPago.choices)

    class Meta:
        db_table = 'factura'
        ordering = ['-fecha']
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'

    def __str__(self):
        return self.numero

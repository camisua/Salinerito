"""Pruebas automáticas de la caja (HU-19 y HU-20)."""
from decimal import Decimal

from django.test import TestCase

from apps.caja import servicios as caja
from apps.caja.models import MetodoPago
from apps.datos_prueba import crear_datos_basicos
from apps.pedidos import servicios
from apps.pedidos.models import Mesa


class CajaTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)
        self.pedido = servicios.crear_pedido(self.mesero, [(self.plato, 2)], mesa=self.mesa)

    def entregar(self):
        for estado in ('EN_PREPARACION', 'LISTO', 'ENTREGADO'):
            servicios.cambiar_estado(self.pedido, estado)

    def test_cobrar_en_efectivo(self):
        """CP-34: genera la factura FV-000001 y la mesa queda libre."""
        self.entregar()
        factura = caja.facturar(self.pedido, self.cajero, MetodoPago.EFECTIVO)
        self.mesa.refresh_from_db()
        self.assertEqual(factura.numero, f'FV-{factura.id:06d}')
        self.assertEqual(factura.total, Decimal('56000'))
        self.assertEqual(self.mesa.estado, Mesa.Estado.LIBRE)

    def test_no_cobra_pedido_sin_entregar(self):
        """CP-35: un pedido que no se ha entregado no se cobra."""
        with self.assertRaisesMessage(caja.ErrorCaja, 'Solo se cobran pedidos entregados'):
            caja.facturar(self.pedido, self.cajero, MetodoPago.EFECTIVO)

    def test_no_cobra_dos_veces(self):
        """CP-36: el mismo pedido no se factura dos veces."""
        self.entregar()
        caja.facturar(self.pedido, self.cajero, MetodoPago.EFECTIVO)
        with self.assertRaisesMessage(caja.ErrorCaja, 'ya fue cobrado'):
            caja.facturar(self.pedido, self.cajero, MetodoPago.TARJETA)

    def test_cierre_de_caja(self):
        """CP-37: el cierre suma por método de pago y cuenta las facturas."""
        self.entregar()
        caja.facturar(self.pedido, self.cajero, MetodoPago.TARJETA)
        cierre = caja.cerrar_caja(self.cajero)
        self.assertEqual(cierre.total_tarjeta, Decimal('56000'))
        self.assertEqual(cierre.total_efectivo, Decimal('0'))
        self.assertEqual(cierre.total_general, Decimal('56000'))
        self.assertEqual(cierre.numero_pedidos, 1)

    def test_cierre_sin_ventas(self):
        """CP-38: sin facturas nuevas el sistema avisa y no crea el cierre."""
        with self.assertRaisesMessage(caja.ErrorCaja, 'No hay facturas nuevas'):
            caja.cerrar_caja(self.cajero)

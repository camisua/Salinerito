"""Pruebas automáticas del inventario (HU-07, HU-08 y HU-18)."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.inventario.models import CompraInsumo, Insumo


class InsumoTests(TestCase):

    def test_minimo_negativo_no_es_valido(self):
        """CP-16: la cantidad mínima no puede ser negativa."""
        insumo = Insumo(nombre='Papa', unidad='kg', existencia=10, cantidad_minima=-1)
        with self.assertRaises(ValidationError):
            insumo.full_clean()

    def test_compra_suma_al_inventario(self):
        """CP-17: el arroz tiene 4 kg, se compran 10 kg y queda en 14 kg."""
        arroz = Insumo.objects.create(nombre='Arroz', unidad='kg', existencia=Decimal('4'), cantidad_minima=5)
        CompraInsumo.objects.create(insumo=arroz, cantidad=Decimal('10'), costo=Decimal('35000'))
        arroz.refresh_from_db()
        self.assertEqual(arroz.existencia, Decimal('14'))

    def test_alerta_de_minimo(self):
        """CP-33: el insumo queda en alerta cuando llega a su cantidad mínima."""
        arroz = Insumo(nombre='Arroz', unidad='kg', existencia=Decimal('4.8'), cantidad_minima=Decimal('5'))
        self.assertTrue(arroz.bajo_minimo)
        arroz.existencia = Decimal('5.2')
        self.assertFalse(arroz.bajo_minimo)

"""Pruebas automáticas de la carta (HU-09 y HU-11)."""
from django.test import TestCase
from django.urls import reverse

from apps.datos_prueba import CLAVE, crear_datos_basicos


class CartaTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)

    def test_plato_con_receta(self):
        """CP-18: el plato queda activo y con los insumos de su receta."""
        self.assertTrue(self.plato.activo)
        self.assertIn(self.arroz, self.plato.insumos.all())

    def test_plato_desactivado_no_sale_en_nuevo_pedido(self):
        """CP-19 y CP-22: el mesero ve los platos activos con precio, no los inactivos."""
        campo = f'name="cantidad_{self.plato.id}"'  # la casilla de cantidad del plato
        self.client.login(username='laura', password=CLAVE)
        respuesta = self.client.get(reverse('nuevo_pedido'))
        self.assertContains(respuesta, campo)
        self.assertContains(respuesta, '28.000')  # el precio se ve en la carta

        self.client.login(username='admin', password=CLAVE)
        self.client.post(reverse('estado_plato', args=[self.plato.pk]))  # botón Desactivar
        self.plato.refresh_from_db()
        self.assertFalse(self.plato.activo)

        self.client.login(username='laura', password=CLAVE)
        self.assertNotContains(self.client.get(reverse('nuevo_pedido')), campo)

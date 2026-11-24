"""Pruebas automáticas de la API REST (HU-15 y HU-16)."""
from django.test import TestCase
from django.urls import reverse

from apps.datos_prueba import CLAVE, crear_datos_basicos
from apps.pedidos import servicios


class ApiTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)
        self.pedido = servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)

    def test_cocina_ve_pedidos_en_json(self):
        """CP-29 y CP-42: la cocina recibe los pedidos en JSON, del más antiguo al más nuevo."""
        self.client.login(username='jorge', password=CLAVE)
        respuesta = self.client.get(reverse('api_cocina'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()[0]['id'], self.pedido.id)

    def test_mesero_no_entra_a_api_cocina(self):
        """CP-42: el mesero recibe acceso denegado (403)."""
        self.client.login(username='laura', password=CLAVE)
        self.assertEqual(self.client.get(reverse('api_cocina')).status_code, 403)

    def test_sin_sesion_no_entra(self):
        """Seguridad: sin iniciar sesión la API no entrega datos."""
        self.assertEqual(self.client.get(reverse('api_platos')).status_code, 403)

    def test_cocina_cambia_estado(self):
        """CP-30: la cocina pasa el pedido a En preparación por la API."""
        self.client.login(username='jorge', password=CLAVE)
        respuesta = self.client.patch(reverse('api_estado_pedido', args=[self.pedido.id]),
                                      {'estado': 'EN_PREPARACION'}, content_type='application/json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['estado'], 'EN_PREPARACION')

    def test_mesero_no_puede_poner_listo(self):
        """CP-43: el mesero no puede marcar un pedido como Listo."""
        self.client.login(username='laura', password=CLAVE)
        respuesta = self.client.patch(reverse('api_estado_pedido', args=[self.pedido.id]),
                                      {'estado': 'LISTO'}, content_type='application/json')
        self.assertEqual(respuesta.status_code, 403)

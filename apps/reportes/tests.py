"""Pruebas automáticas de los reportes (HU-21 y HU-22)."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.caja import servicios as caja
from apps.caja.models import MetodoPago
from apps.datos_prueba import CLAVE, crear_datos_basicos
from apps.pedidos import servicios
from apps.reportes import consultas


class ReportesTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)
        pedido = servicios.crear_pedido(self.mesero, [(self.plato, 2)], mesa=self.mesa)
        for estado in ('EN_PREPARACION', 'LISTO', 'ENTREGADO'):
            servicios.cambiar_estado(pedido, estado)
        caja.facturar(pedido, self.cajero, MetodoPago.EFECTIVO)
        self.hoy = timezone.localdate()

    def test_ventas_por_dia(self):
        """CP-39: la venta de hoy aparece en el día correcto."""
        dias = consultas.ventas_por_dia(self.hoy, self.hoy)
        self.assertEqual(dias[0]['total'], Decimal('56000'))

    def test_estadisticas(self):
        """CP-40: platos más vendidos, ventas por mesero y tiempo de cocina."""
        platos = consultas.platos_mas_vendidos(self.hoy, self.hoy)
        self.assertEqual(platos[0]['plato__nombre'], 'Bandeja paisa')
        self.assertEqual(platos[0]['cantidad_total'], 2)
        self.assertEqual(consultas.ventas_por_mesero(self.hoy, self.hoy)[0]['mesero'], 'Laura')
        self.assertIsNotNone(consultas.tiempo_promedio_cocina(self.hoy, self.hoy))

    def test_exportar_csv(self):
        """CP-41: el administrador descarga el archivo para Excel."""
        self.client.login(username='admin', password=CLAVE)
        respuesta = self.client.get(reverse('reportes_csv'))
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('FV-', respuesta.content.decode('utf-8'))

    def test_solo_el_administrador_ve_reportes(self):
        """Seguridad: el cajero no puede abrir los reportes."""
        self.client.login(username='diana', password=CLAVE)
        self.assertEqual(self.client.get(reverse('reportes')).status_code, 403)

"""Pruebas automáticas de pedidos y cocina (HU-10 y HU-12 a HU-17)."""
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.datos_prueba import CLAVE, crear_datos_basicos
from apps.pedidos import servicios
from apps.pedidos.models import Mesa, Pedido


class MesaTests(TestCase):

    def test_mesa_nueva_queda_libre(self):
        """CP-20: una mesa recién registrada aparece libre."""
        self.assertEqual(Mesa.objects.create(numero=5, capacidad=4).estado, Mesa.Estado.LIBRE)

    def test_mesa_repetida(self):
        """CP-21: no se puede registrar dos veces la misma mesa."""
        Mesa.objects.create(numero=5)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Mesa.objects.create(numero=5)


class PedidoTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)

    def test_pedido_de_mesa(self):
        """CP-23: el pedido queda pendiente y la mesa pasa a ocupada."""
        pedido = servicios.crear_pedido(self.mesero, [(self.plato, 2)], mesa=self.mesa)
        self.mesa.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)
        self.assertEqual(self.mesa.estado, Mesa.Estado.OCUPADA)
        self.assertEqual(pedido.calcular_total(), Decimal('56000'))

    def test_pedido_vacio(self):
        """CP-24: no deja enviar un pedido sin platos."""
        with self.assertRaisesMessage(servicios.ErrorPedido, 'Agrega al menos un plato'):
            servicios.crear_pedido(self.mesero, [], mesa=self.mesa)

    def test_mesa_ocupada(self):
        """Regla extra: no se puede abrir un segundo pedido en una mesa ocupada."""
        servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)
        with self.assertRaisesMessage(servicios.ErrorPedido, 'ya está ocupada'):
            servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)

    def test_pedido_a_domicilio(self):
        """CP-25: el domicilio queda pendiente, marcado como domicilio y con los datos del cliente."""
        datos = {'nombre_cliente': 'Ana Ruiz', 'direccion': 'Calle 5 # 3-20', 'telefono': '3001234567'}
        pedido = servicios.crear_pedido(self.cajero, [(self.plato, 1)], domicilio=datos)
        self.assertEqual(pedido.tipo, Pedido.Tipo.DOMICILIO)
        self.assertEqual(pedido.domicilio.direccion, 'Calle 5 # 3-20')

    def test_domicilio_sin_direccion(self):
        """CP-26: la pantalla exige nombre, dirección y teléfono."""
        self.client.login(username='diana', password=CLAVE)
        respuesta = self.client.post(reverse('nuevo_pedido'), {
            'tipo': 'DOMICILIO', 'nombre_cliente': 'Ana', 'direccion': '', 'telefono': '300',
            f'cantidad_{self.plato.id}': '1',
        })
        self.assertContains(respuesta, 'Completa nombre, dirección y teléfono')
        self.assertEqual(Pedido.objects.count(), 0)

    def test_editar_pedido_pendiente(self):
        """CP-27: un pedido pendiente se puede cambiar."""
        pedido = servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)
        servicios.editar_pedido(pedido, [(self.plato, 3)], 'sin cebolla')
        self.assertEqual(pedido.detalles.get().cantidad, 3)

    def test_no_se_edita_ni_cancela_en_preparacion(self):
        """CP-28: cuando la cocina ya empezó, no se edita ni se cancela."""
        pedido = servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)
        servicios.cambiar_estado(pedido, Pedido.Estado.EN_PREPARACION)
        with self.assertRaises(servicios.ErrorPedido):
            servicios.editar_pedido(pedido, [(self.plato, 2)])
        with self.assertRaises(servicios.ErrorPedido):
            servicios.cambiar_estado(pedido, Pedido.Estado.CANCELADO)

    def test_cancelar_libera_la_mesa(self):
        """Regla extra: al cancelar un pedido pendiente, la mesa vuelve a quedar libre."""
        pedido = servicios.crear_pedido(self.mesero, [(self.plato, 1)], mesa=self.mesa)
        servicios.cambiar_estado(pedido, Pedido.Estado.CANCELADO)
        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.estado, Mesa.Estado.LIBRE)


class CocinaTests(TestCase):

    def setUp(self):
        crear_datos_basicos(self)
        self.pedido = servicios.crear_pedido(self.mesero, [(self.plato, 2)], mesa=self.mesa)

    def test_estados_guardan_la_hora(self):
        """CP-30 y CP-31: cada cambio de estado guarda su hora."""
        servicios.cambiar_estado(self.pedido, Pedido.Estado.EN_PREPARACION)
        servicios.cambiar_estado(self.pedido, Pedido.Estado.LISTO)
        self.pedido.refresh_from_db()
        self.assertIsNotNone(self.pedido.hora_preparacion)
        self.assertIsNotNone(self.pedido.hora_listo)

    def test_no_se_salta_estados(self):
        """Regla extra: no se puede pasar de pendiente directo a entregado."""
        with self.assertRaises(servicios.ErrorPedido):
            servicios.cambiar_estado(self.pedido, Pedido.Estado.ENTREGADO)

    def test_entregar_descuenta_inventario(self):
        """CP-32: 2 bandejas × 0,2 kg = 0,4 kg menos de arroz (14 → 13,6)."""
        for estado in ('EN_PREPARACION', 'LISTO', 'ENTREGADO'):
            servicios.cambiar_estado(self.pedido, estado)
        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.existencia, Decimal('13.6'))

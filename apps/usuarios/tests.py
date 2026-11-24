"""Pruebas automáticas del módulo de usuarios (HU-01 a HU-06).

Cada prueba dice en su comentario a qué caso del plan de pruebas (CP-xx)
corresponde. Se ejecutan con: python manage.py test apps
"""
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.datos_prueba import CLAVE, crear_usuario
from apps.usuarios.models import Usuario


class InicioDeSesionTests(TestCase):

    def setUp(self):
        self.mesero = crear_usuario('laura', Usuario.Rol.MESERO)

    def test_login_correcto(self):
        """CP-01: con datos correctos entra y ve el menú de su rol."""
        respuesta = self.client.post(reverse('login'), {'username': 'laura', 'password': CLAVE}, follow=True)
        self.assertTrue(respuesta.context['user'].is_authenticated)
        self.assertContains(respuesta, 'Mis pedidos')

    def test_login_contrasena_incorrecta(self):
        """CP-02: con la contraseña mal no entra y ve el aviso."""
        respuesta = self.client.post(reverse('login'), {'username': 'laura', 'password': 'mala'})
        self.assertContains(respuesta, 'Usuario o contraseña incorrectos')
        self.assertFalse(respuesta.context['user'].is_authenticated)

    def test_cuenta_desactivada_no_entra(self):
        """CP-03 y CP-14: un usuario desactivado no puede iniciar sesión."""
        self.mesero.is_active = False
        self.mesero.save()
        respuesta = self.client.post(reverse('login'), {'username': 'laura', 'password': CLAVE})
        self.assertFalse(respuesta.context['user'].is_authenticated)

    def test_rol_sin_permiso_recibe_403(self):
        """CP-04: el mesero no puede abrir la carta del administrador."""
        self.client.login(username='laura', password=CLAVE)
        self.assertEqual(self.client.get(reverse('lista_platos')).status_code, 403)

    def test_cerrar_sesion_y_volver_a_entrar(self):
        """CP-05 y CP-06: al cerrar sesión, las páginas internas piden login."""
        self.client.login(username='laura', password=CLAVE)
        self.client.post(reverse('logout'))
        respuesta = self.client.get(reverse('mesas'))
        self.assertRedirects(respuesta, reverse('login') + '?next=' + reverse('mesas'))

    def test_superusuario_siempre_es_administrador(self):
        """Regla del modelo: el superusuario queda con rol ADMINISTRADOR."""
        jefe = Usuario.objects.create_superuser('jefe', 'jefe@prueba.com', CLAVE)
        self.assertEqual(jefe.rol, Usuario.Rol.ADMINISTRADOR)


class MiCuentaTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario('laura', Usuario.Rol.MESERO)
        self.client.login(username='laura', password=CLAVE)

    def test_editar_mis_datos(self):
        """CP-07: el empleado cambia su nombre y su correo."""
        self.client.post(reverse('mi_cuenta'), {
            'guardar_datos': '1', 'first_name': 'Laura', 'last_name': 'Gómez', 'email': 'laura@salinero.com',
        })
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.last_name, 'Gómez')
        self.assertEqual(self.usuario.email, 'laura@salinero.com')

    def test_cambiar_contrasena(self):
        """CP-08: con la contraseña actual correcta, guarda la nueva cifrada."""
        self.client.post(reverse('mi_cuenta'), {
            'cambiar_clave': '1', 'old_password': CLAVE,
            'new_password1': 'Nueva.Clave.99', 'new_password2': 'Nueva.Clave.99',
        })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password('Nueva.Clave.99'))
        self.assertNotEqual(self.usuario.password, 'Nueva.Clave.99')  # no se guarda en texto plano

    def test_contrasena_actual_errada(self):
        """CP-09: si la contraseña actual está mal, no cambia nada."""
        self.client.post(reverse('mi_cuenta'), {
            'cambiar_clave': '1', 'old_password': 'equivocada',
            'new_password1': 'Nueva.Clave.99', 'new_password2': 'Nueva.Clave.99',
        })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(CLAVE))


class GestionUsuariosTests(TestCase):

    def test_usuario_repetido_no_se_crea(self):
        """CP-12: no puede haber dos usuarios con el mismo nombre de usuario."""
        crear_usuario('laura', Usuario.Rol.MESERO)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create_user(username='laura', password=CLAVE, email='otra@prueba.com')

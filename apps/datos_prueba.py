"""Datos de ejemplo que usan las pruebas automáticas.

Cada prueba empieza con una base de datos vacía. Estas funciones crean
lo mínimo que se necesita: usuarios de cada rol, un insumo, un plato
con su receta y una mesa. Así cada archivo tests.py queda corto.
"""
from decimal import Decimal

from apps.carta.models import Categoria, Plato, Receta
from apps.inventario.models import Insumo
from apps.pedidos.models import Mesa
from apps.usuarios.models import Usuario

CLAVE = 'Prueba.2026'  # contraseña de todos los usuarios de prueba


def crear_usuario(username, rol, **extra):
    """Crea un empleado con la contraseña CLAVE."""
    return Usuario.objects.create_user(
        username=username, password=CLAVE, email=f'{username}@prueba.com', rol=rol, **extra
    )


def crear_datos_basicos(prueba):
    """Llena la prueba con usuarios, arroz, una bandeja paisa y la mesa 1.

    Se llama desde setUp(): prueba.mesero, prueba.arroz, prueba.plato, etc.
    """
    prueba.admin = crear_usuario('admin', Usuario.Rol.ADMINISTRADOR)
    prueba.mesero = crear_usuario('laura', Usuario.Rol.MESERO, first_name='Laura')
    prueba.cocina = crear_usuario('jorge', Usuario.Rol.COCINA)
    prueba.cajero = crear_usuario('diana', Usuario.Rol.CAJERO)

    prueba.arroz = Insumo.objects.create(nombre='Arroz', unidad='kg',
                                         existencia=Decimal('14'), cantidad_minima=Decimal('5'))
    categoria = Categoria.objects.create(nombre='Platos fuertes')
    prueba.plato = Plato.objects.create(categoria=categoria, nombre='Bandeja paisa',
                                        precio=Decimal('28000'))
    Receta.objects.create(plato=prueba.plato, insumo=prueba.arroz, cantidad=Decimal('0.2'))
    prueba.mesa = Mesa.objects.create(numero=1)

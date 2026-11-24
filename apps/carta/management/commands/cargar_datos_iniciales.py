"""Carga la carta real de El Salinero, insumos de ejemplo y sus recetas.

Uso:  python manage.py cargar_datos_iniciales
Se puede ejecutar varias veces: no duplica datos.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.carta.models import Categoria, Plato, Receta
from apps.inventario.models import Insumo

# nombre: (unidad, existencia, cantidad mínima)
INSUMOS = {
    'Arroz': ('kg', 20, 5),
    'Frijol': ('kg', 10, 3),
    'Carne de res': ('kg', 15, 5),
    'Chicharrón': ('kg', 6, 2),
    'Pollo': ('kg', 12, 4),
    'Mojarra': ('unidad', 5, 8),
    'Huevo': ('unidad', 60, 24),
    'Plátano': ('unidad', 40, 10),
    'Papa criolla': ('kg', 2, 5),
    'Yuca': ('kg', 10, 3),
    'Mazorca': ('unidad', 20, 6),
    'Aguacate': ('unidad', 15, 5),
    'Arepa': ('unidad', 50, 15),
    'Fruta para jugo': ('kg', 8, 2),
}

# (categoría, plato, precio, {insumo: cantidad por porción})
PLATOS = [
    ('Platos típicos', 'Bandeja Paisa', 38000, {'Arroz': 0.15, 'Frijol': 0.15, 'Carne de res': 0.15, 'Chicharrón': 0.1, 'Huevo': 1, 'Plátano': 1, 'Aguacate': 0.5, 'Arepa': 1}),
    ('Platos típicos', 'Calentao\' Paisa', 17000, {'Arroz': 0.15, 'Frijol': 0.15, 'Huevo': 1, 'Chicharrón': 0.05, 'Arepa': 1}),
    ('Carnes', 'Churrasco Asado', 38000, {'Carne de res': 0.35, 'Papa criolla': 0.2, 'Plátano': 1, 'Arepa': 1}),
    ('Carnes', 'Parrillada 500 g', 55000, {'Carne de res': 0.25, 'Pollo': 0.15, 'Chicharrón': 0.1, 'Papa criolla': 0.2, 'Yuca': 0.2, 'Arepa': 2}),
    ('Pescados', 'Mojarra Frita', 38000, {'Mojarra': 1, 'Arroz': 0.15, 'Plátano': 1, 'Aguacate': 0.5}),
    ('Sopas', 'Ajiaco', 25000, {'Pollo': 0.2, 'Papa criolla': 0.25, 'Mazorca': 1, 'Arroz': 0.1, 'Aguacate': 0.5}),
    ('Sopas', 'Sancocho', 25000, {'Pollo': 0.2, 'Yuca': 0.2, 'Papa criolla': 0.1, 'Mazorca': 1, 'Plátano': 1, 'Arroz': 0.1}),
    ('Desayunos', 'Huevos al gusto', 5000, {'Huevo': 2, 'Arepa': 1}),
    ('Bebidas', 'Jugo en agua', 7000, {'Fruta para jugo': 0.2}),
]


class Command(BaseCommand):
    help = 'Carga la carta de El Salinero, insumos de ejemplo y recetas.'

    @transaction.atomic
    def handle(self, *args, **options):
        for nombre, (unidad, existencia, minima) in INSUMOS.items():
            Insumo.objects.get_or_create(
                nombre=nombre,
                defaults={'unidad': unidad, 'existencia': existencia, 'cantidad_minima': minima},
            )
        for cat_nombre, plato_nombre, precio, receta in PLATOS:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
            plato, _ = Plato.objects.get_or_create(
                nombre=plato_nombre, defaults={'categoria': categoria, 'precio': precio},
            )
            for insumo_nombre, cantidad in receta.items():
                Receta.objects.get_or_create(
                    plato=plato, insumo=Insumo.objects.get(nombre=insumo_nombre),
                    defaults={'cantidad': Decimal(str(cantidad))},
                )
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Insumo.objects.count()} insumos, {Categoria.objects.count()} categorías, '
            f'{Plato.objects.count()} platos y {Receta.objects.count()} ingredientes de receta.'
        ))

"""Crea las mesas del salón. Uso: python manage.py crear_mesas 12"""
from django.core.management.base import BaseCommand

from apps.pedidos.models import Mesa


class Command(BaseCommand):
    help = 'Crea las mesas numeradas del 1 al N (por defecto 12).'

    def add_arguments(self, parser):
        parser.add_argument('cantidad', type=int, nargs='?', default=12)

    def handle(self, *args, **options):
        for numero in range(1, options['cantidad'] + 1):
            Mesa.objects.get_or_create(numero=numero)
        self.stdout.write(self.style.SUCCESS(f'Hay {Mesa.objects.count()} mesas.'))

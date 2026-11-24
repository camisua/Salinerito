from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Empleado del restaurante.

    Hereda de AbstractUser el nombre de usuario, la contraseña cifrada,
    el nombre, el apellido, el correo y si la cuenta está activa.
    Le agregamos el rol, que define qué pantallas puede usar.
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        MESERO = 'MESERO', 'Mesero'
        COCINA = 'COCINA', 'Cocina'
        CAJERO = 'CAJERO', 'Cajero'

    email = models.EmailField('correo electrónico', unique=True)
    rol = models.CharField('rol', max_length=20, choices=Rol.choices, default=Rol.MESERO)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'

    def save(self, *args, **kwargs):
        # El superusuario siempre tiene rol de administrador
        if self.is_superuser:
            self.rol = self.Rol.ADMINISTRADOR
        super().save(*args, **kwargs)

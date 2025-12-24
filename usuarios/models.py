#crear modelo usuario
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('analista', 'Analista'),
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='analista'
    )

    nombre_completo = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} - {self.rol}"

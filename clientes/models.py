from django.db import models

# clientes/models.py
from django.db import models

class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateField(auto_now_add=True)
    nivel_riesgo = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"


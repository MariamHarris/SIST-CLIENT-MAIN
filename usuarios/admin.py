from django.contrib import admin

# Registrar el modelo en el admin
from django.contrib import admin
from .models import Usuario
admin.site.register(Usuario)

from django.urls import path

from . import views
from .views import importar_clientes

app_name = 'clientes'

urlpatterns = [
    path('importar/', importar_clientes, name='importar'),
    path('', views.clientes_list, name='index'),
    path('', views.clientes_list, name='listar'),
    path('crear/', views.cliente_create, name='crear'),
    path('editar/<int:pk>/', views.cliente_update, name='editar'),
    path('eliminar/<int:pk>/', views.cliente_delete, name='eliminar'),
]
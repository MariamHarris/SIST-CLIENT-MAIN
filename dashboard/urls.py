from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.inicio, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('reportes/', views.reportes, name='reportes'),
]

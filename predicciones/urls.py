from django.urls import path

from . import views

app_name = 'predicciones'

urlpatterns = [
    path('', views.home, name='index'),
    path('entrenar-modelo/', views.entrenar_modelo, name='entrenar_modelo'),
    path('predecir-abandono/<int:cliente_id>/', views.predecir_abandono, name='predecir_abandono'),
    path('calcular-riesgo/<int:cliente_id>/', views.calcular_nivel_riesgo, name='calcular_riesgo'),
]

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('conversacion/', views.conversacion, name='conversacion'),
    path('historial/', views.historial_chat, name='historial'),
    path('api/chat/', views.api_chat, name='api_chat'),
]
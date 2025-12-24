"""
URL configuration for sist_pred_client project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

# Función 'inicio' 
def inicio(request):
    return redirect('usuarios:login')
urlpatterns = [
    path('', inicio, name='inicio'), 
    path('login/', lambda request: redirect('usuarios:login'), name='login'),
    path('logout/', lambda request: redirect('usuarios:logout'), name='logout'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('clientes/', include('clientes.urls')),

    path('predicciones/', include('predicciones.urls')),
    path('chatbot/', include('chatbot.urls')),

]

# sist_pred_client
handler403 = 'sist_pred_client.views.custom_permission_denied'

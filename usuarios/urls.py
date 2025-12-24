from django.urls import path
from .views import CustomLoginView, CustomLogoutView


from .views import (
    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioDeleteView,
)
app_name = 'usuarios'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', UsuarioListView.as_view(), name='index'),
    path('', UsuarioListView.as_view(), name='listar'),
    path('crear/', UsuarioCreateView.as_view(), name='crear'),
    path('editar/<int:pk>/', UsuarioUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', UsuarioDeleteView.as_view(), name='eliminar'),
]

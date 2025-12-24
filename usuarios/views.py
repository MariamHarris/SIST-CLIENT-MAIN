from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .decorators import role_required
from .forms import UsuarioForm
from .mixins import AdminRequiredMixin
from .models import Usuario
from .utils import sync_user_group

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            sync_user_group(self.request.user)
        except Exception:
            # No bloquear el login por un tema de grupos
            pass
        return response

    def get_success_url(self):
        user = self.request.user

        if getattr(user, 'rol', None) == 'admin' or user.is_superuser:
            return reverse_lazy('dashboard:index')
        return reverse_lazy('dashboard:index')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('usuarios:login')


#vistas crud
class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'


class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/forms.html'
    success_url = reverse_lazy('usuarios:listar')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        sync_user_group(self.object)
        return response


class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/forms.html'
    success_url = reverse_lazy('usuarios:listar')

    def form_valid(self, form):
        response = super().form_valid(form)
        sync_user_group(self.object)
        return response


class UsuarioDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model = Usuario
    template_name = 'usuarios/confirm_delete.html'
    success_url = reverse_lazy('usuarios:listar')

@login_required
@role_required(roles=['admin'])
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')
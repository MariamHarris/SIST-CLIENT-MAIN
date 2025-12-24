from __future__ import annotations

import re

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy

from .decorators import role_required
from .forms import ClienteForm
from .models import Cliente

@login_required
def home(request):
    return redirect('clientes:index')

@login_required
def importar_clientes(request):
    if not getattr(request.user, 'is_superuser', False) and getattr(request.user, 'rol', None) != 'admin':
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('dashboard:inicio')

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            # Leer archivo con pandas
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            elif archivo.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(archivo)
            else:
                messages.error(request, "Formato de archivo no soportado.")
                return redirect('clientes:importar')

            # Validación de datos
            errores = []
            for _, row in df.iterrows():
                email = str(row.get('email', '')).strip()
                nombre = str(row.get('nombre', '')).strip()
                apellido = str(row.get('apellido', '')).strip()
                
                # Campos obligatorios
                if not nombre or not apellido or not email:
                    errores.append(f"Fila con email {email} tiene campos obligatorios vacíos.")
                    continue

                # Validar email simple
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    errores.append(f"Email inválido: {email}")
                    continue

                # Evitar duplicados
                if Cliente.objects.filter(email=email).exists():
                    errores.append(f"Email duplicado: {email}")
                    continue

                # Guardar cliente
                Cliente.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    telefono=row.get('telefono', ''),
                    direccion=row.get('direccion', ''),
                    estado=row.get('estado', 'activo'),
                    nivel_riesgo=row.get('nivel_riesgo', 0.0)
                )

            if errores:
                for err in errores:
                    messages.error(request, err)
            else:
                messages.success(request, "Clientes importados correctamente.")

        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")

        return redirect('clientes:importar')

    return render(request, 'clientes/importar.html')

@login_required
@role_required(roles=['admin', 'analista'])
def clientes_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/list.html', {'clientes': clientes})

@login_required
@role_required(roles=['admin'])
def cliente_create(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('clientes:index')
    return render(request, 'clientes/form.html', {'form': form})

# Modificar cliente (solo admin)
@login_required
@role_required(roles=['admin'])
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes:index')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'object': cliente})
# Eliminar cliente (solo admin)
@login_required
@role_required(roles=['admin'])
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes:index')
    return render(request, 'clientes/confirm_delete.html', {'object': cliente, 'cliente': cliente})

# Protege todas las vistas con login_required
@method_decorator(login_required, name='dispatch')
class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/list.html'
    context_object_name = 'clientes'

@method_decorator(login_required, name='dispatch')
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:list')

@method_decorator(login_required, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:list')

@method_decorator(login_required, name='dispatch')
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_delete.html'
    success_url = reverse_lazy('clientes:list')
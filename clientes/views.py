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

            # Normalizar nombres de columnas para validar/leer sin depender de mayúsculas/espacios
            df.columns = [str(c).strip().lower() for c in df.columns]

            required_cols = {'nombre', 'apellido', 'email'}
            missing = sorted(required_cols - set(df.columns))
            if missing:
                messages.error(
                    request,
                    "Faltan columnas obligatorias: " + ", ".join(missing) + ". "
                    "Columnas requeridas: nombre, apellido, email.",
                )
                return redirect('clientes:importar')

            def _clean_str(value) -> str:
                if value is None:
                    return ''
                try:
                    if pd.isna(value):
                        return ''
                except Exception:
                    pass
                return str(value).strip()

            # Validación de datos
            errores = []
            for idx, row in df.iterrows():
                fila_num = int(idx) + 2  # +2: header(1) + 1-based row
                email = _clean_str(row.get('email', ''))
                nombre = _clean_str(row.get('nombre', ''))
                apellido = _clean_str(row.get('apellido', ''))
                
                # Campos obligatorios
                if not nombre or not apellido or not email:
                    errores.append(f"Fila {fila_num}: campos obligatorios vacíos (nombre/apellido/email).")
                    continue

                # Validar email simple
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    errores.append(f"Fila {fila_num}: email inválido: {email}")
                    continue

                # Evitar duplicados
                if Cliente.objects.filter(email=email).exists():
                    errores.append(f"Fila {fila_num}: email duplicado: {email}")
                    continue

                # Guardar cliente
                raw_riesgo = row.get('nivel_riesgo', '')
                nivel_riesgo = 'Bajo'
                probabilidad_abandono = 0.0

                if raw_riesgo is not None:
                    raw_riesgo_str = _clean_str(raw_riesgo)
                    raw_riesgo_norm = raw_riesgo_str.lower()

                    if raw_riesgo_norm in {'bajo', 'medio', 'alto'}:
                        nivel_riesgo = raw_riesgo_norm.capitalize()
                    else:
                        try:
                            val = float(raw_riesgo_str)
                            # Acepta probabilidad 0..1 o porcentaje 0..100
                            probabilidad_abandono = val / 100.0 if val > 1 else val
                            if probabilidad_abandono < 0:
                                probabilidad_abandono = 0.0
                            if probabilidad_abandono > 1:
                                probabilidad_abandono = 1.0

                            if probabilidad_abandono < 0.33:
                                nivel_riesgo = 'Bajo'
                            elif probabilidad_abandono < 0.66:
                                nivel_riesgo = 'Medio'
                            else:
                                nivel_riesgo = 'Alto'
                        except (TypeError, ValueError):
                            pass

                estado = _clean_str(row.get('estado', 'activo')).lower() or 'activo'
                if estado not in {'activo', 'inactivo'}:
                    estado = 'activo'

                Cliente.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    telefono=_clean_str(row.get('telefono', '')),
                    direccion=_clean_str(row.get('direccion', '')),
                    estado=estado,
                    nivel_riesgo=nivel_riesgo,
                    probabilidad_abandono=probabilidad_abandono,
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
    riesgo = (request.GET.get('riesgo') or '').strip()
    orden = (request.GET.get('orden') or '').strip()

    clientes_qs = Cliente.objects.all()
    if riesgo in {'Bajo', 'Medio', 'Alto'}:
        clientes_qs = clientes_qs.filter(nivel_riesgo=riesgo)

    if orden == 'prob_asc':
        clientes_qs = clientes_qs.order_by('probabilidad_abandono', 'apellido', 'nombre')
    elif orden == 'prob_desc':
        clientes_qs = clientes_qs.order_by('-probabilidad_abandono', 'apellido', 'nombre')
    elif orden == 'nombre':
        clientes_qs = clientes_qs.order_by('apellido', 'nombre')

    clientes = list(clientes_qs)
    for c in clientes:
        try:
            c.probabilidad_pct = round(float(c.probabilidad_abandono or 0.0) * 100.0, 1)
        except (TypeError, ValueError):
            c.probabilidad_pct = 0.0

    total_clientes = Cliente.objects.count()
    total_alto = Cliente.objects.filter(nivel_riesgo='Alto').count()
    total_medio = Cliente.objects.filter(nivel_riesgo='Medio').count()
    total_bajo = Cliente.objects.filter(nivel_riesgo='Bajo').count()
    total_activos = Cliente.objects.filter(estado='activo').count()

    return render(
        request,
        'clientes/list.html',
        {
            'clientes': clientes,
            'filtro_riesgo': riesgo,
            'orden': orden,
            'stats': {
                'total_clientes': total_clientes,
                'total_alto': total_alto,
                'total_medio': total_medio,
                'total_bajo': total_bajo,
                'total_activos': total_activos,
            },
        },
    )

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
    success_url = reverse_lazy('clientes:index')

@method_decorator(login_required, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:index')

@method_decorator(login_required, name='dispatch')
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_delete.html'
    success_url = reverse_lazy('clientes:index')
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


@login_required
def index(request):
    return render(request, 'chatbot/index.html')


@login_required
def conversacion(request):
    # Vista simple: mantiene compatibilidad con rutas definidas
    return render(request, 'chatbot/index.html')


@login_required
def historial_chat(request):
    # Si no hay persistencia, mostrar UI base con estado vacío
    return render(request, 'chatbot/index.html')


@login_required
def api_chat(request):
    return JsonResponse({'error': 'Endpoint no implementado'}, status=501)


# Backwards-compatible alias
home = index

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

import json
import re
import unicodedata

from django.db.models import Q


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
    if request.method not in {"GET", "POST"}:
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if request.method == "GET":
        return JsonResponse(
            {
                "reply": (
                    "Hola. Puedo ayudarte con: importar clientes (CSV/Excel), "
                    "predicciones, nivel de riesgo, usuarios/roles, y navegación del sistema. "
                    "Escribe una pregunta."
                )
            }
        )

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"reply": "Escribe un mensaje para poder ayudarte."}, status=400)

    def _normalize(text: str) -> str:
        text = text.strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return text

    normalized = _normalize(message)

    # Dataset-driven Q&A (no external APIs)
    try:
        from clientes.models import Cliente
    except Exception:
        Cliente = None  # type: ignore

    def _prediction_explanation() -> str:
        return (
            "La predicción calcula una probabilidad de abandono (0% a 100%). "
            "Luego se clasifica el riesgo: Bajo (<33%), Medio (33%–66%), Alto (>66%)."
        )

    if Cliente is not None:
        # 1) "¿Cuántos clientes tengo?"
        if ("cuantos" in normalized or "cuantas" in normalized) and "cliente" in normalized:
            total = Cliente.objects.count()
            if "riesgo" in normalized and "alto" in normalized:
                total_alto = Cliente.objects.filter(nivel_riesgo='Alto').count()
                return JsonResponse({"reply": f"Tienes {total_alto} clientes en riesgo Alto (de {total} en total)."})
            return JsonResponse({"reply": f"Tienes {total} clientes cargados en el sistema."})

        # 2) "¿Cuántos están en riesgo alto?" (sin decir clientes)
        if ("riesgo" in normalized and "alto" in normalized) and ("cuantos" in normalized or "cuantas" in normalized):
            total_alto = Cliente.objects.filter(nivel_riesgo='Alto').count()
            return JsonResponse({"reply": f"Hay {total_alto} clientes en riesgo Alto."})

        # 3) "Dame el riesgo del cliente X" (id / email / nombre)
        if "riesgo" in normalized and "cliente" in normalized:
            client_qs = Cliente.objects.all()

            # By email
            email_match = re.search(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+", message)
            if email_match:
                email = email_match.group(0).strip()
                client_qs = client_qs.filter(email__iexact=email)
            else:
                # By id
                id_match = re.search(r"\bcliente\s+(\d+)\b", normalized)
                if id_match:
                    client_qs = client_qs.filter(pk=int(id_match.group(1)))
                else:
                    # By name: take text after "cliente"
                    tail = normalized.split("cliente", 1)[-1].strip()
                    tail = tail.strip(":,-. ")
                    if tail:
                        client_qs = client_qs.filter(
                            Q(nombre__icontains=tail) | Q(apellido__icontains=tail)
                        )

            matches = list(client_qs[:5])
            if not matches:
                return JsonResponse({"reply": "No encontré ese cliente. Prueba con el ID, el email o el nombre/apellido."})
            if len(matches) > 1:
                opciones = ", ".join(f"{c.pk}: {c.nombre} {c.apellido}" for c in matches[:3])
                return JsonResponse({"reply": f"Encontré varios. Sé más específico. Opciones: {opciones}."})

            c = matches[0]
            prob = 0.0
            try:
                prob = float(c.probabilidad_abandono or 0.0)
            except (TypeError, ValueError):
                prob = 0.0
            prob_pct = round(prob * 100.0, 1)
            return JsonResponse(
                {
                    "reply": (
                        f"El cliente {c.nombre} {c.apellido} tiene riesgo {c.nivel_riesgo} "
                        f"con probabilidad de abandono {prob_pct}%. "
                        + _prediction_explanation()
                    )
                }
            )

        # 4) Explicación general
        if "explica" in normalized and ("predic" in normalized or "riesgo" in normalized):
            return JsonResponse({"reply": _prediction_explanation()})

    faqs: list[tuple[list[str], str]] = [
        (
            ["hola", "buenas", "hey", "que tal"],
            "¡Hola! ¿Qué necesitas? (importar clientes, predicciones, riesgo, usuarios/roles)",
        ),
        (
            ["ayuda", "help", "que puedes", "que haces"],
            "Puedo ayudarte con: importar clientes (CSV/Excel), predicciones, nivel de riesgo, usuarios/roles.",
        ),
        (
            ["importar", "excel", "csv", "archivo"],
            "Para importar: ve a Clientes → Importar. Sube un CSV o Excel. Si incluyes 'nivel_riesgo', puede ser 'Bajo/Medio/Alto' o un número (0..1 o 0..100).",
        ),
        (
            ["predic", "predec", "modelo", "ml"],
            "Para predecir: entra a Predicciones y usa el botón 'Predecir'. El sistema calcula la probabilidad de abandono y guarda el nivel de riesgo en el cliente.",
        ),
        (
            ["riesgo", "alto", "medio", "bajo", "probabilidad"],
            "El nivel de riesgo se clasifica como Bajo/Medio/Alto según la probabilidad de abandono. También se guarda la probabilidad como número para ordenar/analizar.",
        ),
        (
            ["usuario", "rol", "admin", "analista", "permiso", "login"],
            "Si tienes problemas de acceso, revisa tu rol (admin/analista). Para entrar, usa el login y asegúrate de tener usuario creado (puedes crear uno desde el admin).",
        ),
    ]

    best_score = 0
    best_answer = "No estoy seguro. Prueba preguntando por: importar clientes, predicciones, riesgo o usuarios/roles."
    for keywords, answer in faqs:
        score = 0
        for kw in keywords:
            if kw in normalized:
                score += 1
        if score > best_score:
            best_score = score
            best_answer = answer

    return JsonResponse({"reply": best_answer})


# Backwards-compatible alias
home = index

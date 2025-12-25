from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render

from clientes.models import Cliente


@login_required
def home(request):
    clientes = Cliente.objects.all().order_by('id')[:200]
    can_train = bool(getattr(request.user, 'is_superuser', False) or getattr(request.user, 'rol', None) == 'admin')
    return render(
        request,
        'predicciones/inicio.html',
        {
            'clientes': clientes,
            'can_train': can_train,
            'page_title': 'Predicciones',
            'page_subtitle': 'Selecciona un cliente para analizar riesgo',
        },
    )

@login_required
def entrenar_modelo(request):
    if not request.user.is_superuser and getattr(request.user, 'rol', None) != 'admin':
        return HttpResponseForbidden("No tienes permiso para entrenar el modelo")

    try:
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder
        import joblib
    except ModuleNotFoundError as exc:
        return JsonResponse(
            {
                'error': 'Dependencias de ML no instaladas (pandas/sklearn/joblib).',
                'detalle': str(exc),
            },
            status=500,
        )

    
    # 1) Preparar dataset
    clientes = Cliente.objects.all().values('estado', 'nivel_riesgo', 'telefono')
    df = pd.DataFrame(clientes)

    if df.empty:
        return JsonResponse({'error': 'No hay datos de clientes para entrenar'}, status=400)

    # Target: churn = 1 si estado == inactivo
    y = (df['estado'].fillna('activo').astype(str).str.lower() == 'inactivo').astype(int)
    if int(y.sum()) == 0:
        return JsonResponse({'error': 'No hay clientes inactivos para entrenar'}, status=400)

    X = pd.DataFrame({
        'nivel_riesgo': df.get('nivel_riesgo', 'Bajo').fillna('Bajo').astype(str),
        'tiene_telefono': df.get('telefono', '').fillna('').astype(str).str.strip().ne('').astype(int),
    })

    # 3. Separar train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4) Entrenar modelo (pipeline estable)
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['nivel_riesgo']),
        ],
        remainder='passthrough',
    )
    modelo = Pipeline(
        steps=[
            ('preprocess', preprocessor),
            ('clf', LogisticRegression(max_iter=1000)),
        ]
    )
    modelo.fit(X_train, y_train)

    # 5) Evaluar métricas
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)[:, 1]
    acc = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    try:
        roc = float(roc_auc_score(y_test, y_proba))
    except ValueError:
        roc = None

    # 6) Guardar modelo
    joblib.dump(modelo, 'predicciones/modelo_cliente.pkl')

    return JsonResponse({
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc,
    })


@login_required
def predecir_abandono(request, cliente_id):
    if not request.user.is_superuser and getattr(request.user, 'rol', None) not in {'admin', 'analista'}:
        return HttpResponseForbidden("No tienes permiso para hacer predicciones")

    try:
        import pandas as pd
        import joblib
    except ModuleNotFoundError as exc:
        return JsonResponse(
            {
                'error': 'Dependencias de ML no instaladas (pandas/joblib).',
                'detalle': str(exc),
            },
            status=500,
        )
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

    # Cargar modelo
    try:
        modelo = joblib.load('predicciones/modelo_cliente.pkl')
    except FileNotFoundError:
        return JsonResponse({'error': 'Modelo no entrenado'}, status=400)

    df = pd.DataFrame([
        {
            'nivel_riesgo': cliente.nivel_riesgo,
            'tiene_telefono': 1 if (cliente.telefono or '').strip() else 0,
        }
    ])
    probabilidad = float(modelo.predict_proba(df)[:, 1][0])

    return JsonResponse({
        'cliente': cliente.nombre,
        'probabilidad_abandono': round(probabilidad * 100, 2)
    })

@login_required
def calcular_nivel_riesgo(request, cliente_id):
    if not request.user.is_superuser and getattr(request.user, 'rol', None) not in {'admin', 'analista'}:
        return HttpResponseForbidden("No tienes permiso para esto")

    try:
        import pandas as pd
        import joblib
    except ModuleNotFoundError as exc:
        return JsonResponse(
            {
                'error': 'Dependencias de ML no instaladas (pandas/joblib).',
                'detalle': str(exc),
            },
            status=500,
        )
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

    # Cargar modelo
    try:
        modelo = joblib.load('predicciones/modelo_cliente.pkl')
    except FileNotFoundError:
        return JsonResponse({'error': 'Modelo no entrenado'}, status=400)

    df = pd.DataFrame([
        {
            'nivel_riesgo': cliente.nivel_riesgo,
            'tiene_telefono': 1 if (cliente.telefono or '').strip() else 0,
        }
    ])
    probabilidad = float(modelo.predict_proba(df)[:, 1][0])

    # Calcular nivel de riesgo
    if probabilidad < 0.33:
        nivel = "Bajo"
    elif probabilidad < 0.66:
        nivel = "Medio"
    else:
        nivel = "Alto"

    # Guardar en el cliente (para listado/orden por probabilidad)
    cliente.probabilidad_abandono = probabilidad
    cliente.nivel_riesgo = nivel
    cliente.save()

    return JsonResponse({
        'cliente': cliente.nombre,
        'probabilidad_abandono': round(probabilidad*100,2),
        'nivel_riesgo': nivel
    })
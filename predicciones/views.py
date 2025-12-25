from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from clientes.models import Cliente


@login_required
def home(request):
    clientes = Cliente.objects.all().order_by('id')[:200]
    return render(request, 'predicciones/inicio.html', {'clientes': clientes})

@login_required
def entrenar_modelo(request):
    if not request.user.is_superuser and getattr(request.user, 'rol', None) != 'admin':
        return HttpResponseForbidden("No tienes permiso para entrenar el modelo")

    try:
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
        from sklearn.model_selection import train_test_split
        import joblib
    except ModuleNotFoundError as exc:
        return JsonResponse(
            {
                'error': 'Dependencias de ML no instaladas (pandas/sklearn/joblib).',
                'detalle': str(exc),
            },
            status=500,
        )

    
    # 1. Preparar dataset
    
    clientes = Cliente.objects.all().values(
        'estado', 'nivel_riesgo', 'telefono'  # ajusta según tus features
    )
    df = pd.DataFrame(clientes)

    # Convertir variables categóricas si es necesario
    df = pd.get_dummies(df, columns=['estado', 'nivel_riesgo'], drop_first=True)

    # 2. Definir X y y (ejemplo: predecir abandono por estado)
    # Supongamos que abandono = estado_inactivo (1) / activo (0)
    if 'estado_inactivo' in df.columns:
        y = df['estado_inactivo']
        X = df.drop(columns=['estado_inactivo'])
    else:
        return JsonResponse({'error': 'No hay clientes inactivos para entrenar'}, status=400)

    # 3. Separar train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4. Entrenar modelo
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # 5. Evaluar métricas
    y_pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    roc = roc_auc_score(y_test, modelo.predict_proba(X_test)[:, 1])

    # 6. Guardar modelo
    joblib.dump(modelo, 'predicciones/modelo_cliente.pkl')

    return JsonResponse({
        'accuracy': acc,
        'roc_auc': roc,
        'report': report
    })

@login_required
def predecir_abandono(request, cliente_id):
    # Permisos
    if not request.user.is_superuser and getattr(request.user, 'rol', None) not in {'admin', 'analista'}:
        return HttpResponseForbidden("No tienes permiso para hacer predicciones")

    # Dependencias ML
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

    # Cliente
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

    # Modelo
    try:
        modelo = joblib.load('predicciones/modelo_cliente.pkl')
    except FileNotFoundError:
        return JsonResponse({'error': 'Modelo no entrenado'}, status=400)

    # DataFrame
    df = pd.DataFrame([{
        'telefono': cliente.telefono,
        'estado': cliente.estado,
        'nivel_riesgo': float(cliente.nivel_riesgo),
    }])

    df = pd.get_dummies(df, columns=['estado'], drop_first=True)

    # Alinear columnas con el modelo
    for col in modelo.feature_names_in_:
        if col not in df.columns:
            df[col] = 0
    df = df[modelo.feature_names_in_]

    # Predicción
    probabilidad = float(modelo.predict_proba(df)[:, 1][0]) * 100

    # GUARDAR RESULTADOS (ESTO ES LA CLAVE)
    cliente.probabilidad_abandono = round(probabilidad, 2)

    # Nivel de riesgo simple
    if probabilidad >= 70:
        cliente.nivel_riesgo = 3
    elif probabilidad >= 40:
        cliente.nivel_riesgo = 2
    else:
        cliente.nivel_riesgo = 1

    cliente.save()

    # Volver al dashboard (NO JSON)
    return redirect('dashboard:inicio')

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

    # Preparar datos del cliente como dataframe
    df = pd.DataFrame([{
        'telefono': cliente.telefono,
        'estado': cliente.estado,
        'nivel_riesgo': cliente.nivel_riesgo,  # si ya existía, para consistencia
    }])

    df = pd.get_dummies(df, columns=['estado', 'nivel_riesgo'], drop_first=True)

    # Asegurarse que las columnas coincidan con el modelo
    modelo_cols = modelo.feature_names_in_
    for col in modelo_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[modelo_cols]

    # Predicción
    probabilidad = modelo.predict_proba(df)[:, 1][0]

    # Calcular nivel de riesgo
    if probabilidad < 0.3:
        nivel = "Bajo"
    elif probabilidad < 0.6:
        nivel = "Medio"
    else:
        nivel = "Alto"

    # Guardar en el cliente (opcional)
    cliente.nivel_riesgo = nivel
    cliente.save()

    return JsonResponse({
        'cliente': cliente.nombre,
        'probabilidad_abandono': round(probabilidad*100,2),
        'nivel_riesgo': nivel
    })
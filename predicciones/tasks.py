from celery import shared_task
import joblib
from django.conf import settings
from usuarios.models import Alert
from clientes.models import Cliente
import pandas as pd

@shared_task
def detect_high_risk_alerts(model_path=None, threshold=0.8, batch_limit=1000):
    model_path = model_path or getattr(settings, "CHURN_MODEL_PATH", "models/churn_v1.joblib")
    try:
        model = joblib.load(model_path)
    except Exception as e:
        return {"error": str(e)}

    # Cargar features de clientes (ajusta según tu modelo/fields)
    qs = Cliente.objects.all()[:batch_limit]
    if not qs:
        return {"ok": True, "created": 0}
    df = pd.DataFrame([{
        "id": c.id,
        # añade aquí las columnas que usa tu modelo; este es un placeholder
        "feature1": getattr(c, "feature1", 0),
        "feature2": getattr(c, "feature2", 0),
    } for c in qs]).set_index("id")

    X = df.values
    probs = model.predict_proba(X)[:,1] if hasattr(model, "predict_proba") else model.predict(X)
    created = 0
    for cid, p in zip(df.index.tolist(), probs.tolist()):
        if p >= threshold:
            # evita duplicados recientes: crea siempre o aplicar lógica para no duplicar
            cliente = Cliente.objects.get(pk=cid)
            Alert.objects.create(cliente=cliente, probability=float(p))
            created += 1
    return {"ok": True, "created": created}

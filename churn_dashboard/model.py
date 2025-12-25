"""Modelo de predicción de churn y utilidades de entrenamiento.

Funciones principales:
- entrenar_modelo(df, features, target)
- guardar_modelo(model, path)
- cargar_modelo(path)
- predecir_proba(model, X)

Usa RandomForestClassifier por defecto y joblib para persistencia.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
import joblib
import json


MODEL_PATH = Path('churn_model.joblib')


def _prepare_Xy(df: pd.DataFrame, features, target):
    X = df[features].copy()
    # Rellena/encode básico
    X = X.fillna(0)
    y = df[target].astype(int)
    return X, y


def entrenar_modelo(df: pd.DataFrame, features, target='Churn'):
    """Entrena un RandomForest y devuelve (modelo, metrics).

    metrics incluye: confusion_matrix, classification_report, roc_auc, feature_importances
    """
    X, y = _prepare_Xy(df, features, target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1] if hasattr(clf, 'predict_proba') else None

    cm = confusion_matrix(y_test, y_pred).tolist()
    cr = classification_report(y_test, y_pred, output_dict=True)
    roc = float(roc_auc_score(y_test, y_proba)) if y_proba is not None and len(np.unique(y_test)) > 1 else None

    fi = None
    try:
        fi = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
    except Exception:
        fi = None

    metrics = {
        'confusion_matrix': cm,
        'classification_report': cr,
        'roc_auc': roc,
        'feature_importances': fi.to_dict() if fi is not None else None
    }

    return clf, metrics


def guardar_modelo(model, path: str = None):
    p = Path(path) if path else MODEL_PATH
    joblib.dump(model, p)
    return str(p)


def cargar_modelo(path: str = None):
    p = Path(path) if path else MODEL_PATH
    if not p.exists():
        raise FileNotFoundError(f"No se encontró el modelo en {p}")
    return joblib.load(p)


def predecir_proba(model, X: pd.DataFrame):
    """Devuelve la probabilidad de churn (0-100) y la clasificación binaria."""
    X = X.fillna(0)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else model.predict(X)
    return (proba * 100).round(2)


def top_features_contrib(model, X_row: pd.DataFrame, features: list, top_n=5):
    """Devuelve las `top_n` características por importancia global para explicar la predicción.

    Nota: Aquí usamos importancias globales del modelo como proxy. Para explicaciones locales,
    se recomienda integrar SHAP (no incluido por simplicidad).
    """
    try:
        importances = model.feature_importances_
        s = pd.Series(importances, index=features).sort_values(ascending=False)
        top = s.head(top_n)
        # Formatear impacto relativo simple
        return [(k, float(v)) for k,v in top.items()]
    except Exception:
        return []
# model.py - Entrenamiento y predicción ML

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
import joblib

def entrenar_modelo(df, features, target, algoritmo='rf'):
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
    if algoritmo == 'rf':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:,1]
    metrics = {
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'classification_report': classification_report(y_test, y_pred, output_dict=True),
        'roc_auc': roc_auc_score(y_test, y_proba),
        'roc_curve': roc_curve(y_test, y_proba),
        'feature_importances': getattr(model, 'feature_importances_', None)
    }
    return model, metrics

def predecir_cliente(model, cliente_df, features):
    proba = model.predict_proba(cliente_df[features])[:,1][0]
    pred = int(proba > 0.5)
    return proba, pred

def guardar_modelo(model, path='modelo_churn.pkl'):
    joblib.dump(model, path)

def cargar_modelo(path='modelo_churn.pkl'):
    return joblib.load(path)

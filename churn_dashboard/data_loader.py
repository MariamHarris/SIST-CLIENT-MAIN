"""Carga de datos y utilidades para el dashboard.
Soporta carga desde CSV (si existe) o crea un conjunto de ejemplo minimal.
Todas las funciones devuelven un pandas.DataFrame con columnas esperadas.
"""
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


def _sample_dataframe(n=200):
    # Crea un DataFrame de ejemplo con las columnas requeridas
    import numpy as np
    ids = [f'C{i:04d}' for i in range(1, n+1)]
    nombres = [f'Cliente {i}' for i in range(1, n+1)]
    antig = np.random.randint(1, 60, size=n)
    valor = np.round(np.random.uniform(10, 200, size=n), 2)
    ult = [datetime.now() - timedelta(days=int(x)) for x in np.random.randint(0, 90, size=n)]
    estado = ['Activo' if x else 'Inactivo' for x in np.random.choice([1,0], size=n, p=[0.85,0.15])]
    freq = np.random.randint(0, 60, size=n)
    inter30 = np.random.randint(0, 20, size=n)
    uso_ult_mes = np.round(np.random.uniform(0,1,size=n),2)
    churn = np.random.choice([0,1], size=n, p=[0.9,0.1])
    segmento = pd.cut(antig, bins=[0,6,24,999], labels=['Nuevo','Medio','Antiguo'])

    df = pd.DataFrame({
        'ID_Cliente': ids,
        'Nombre': nombres,
        'Antigüedad': antig,
        'Valor_Mensual': valor,
        'Última_Interacción': ult,
        'Estado_Actual': estado,
        'Frecuencia_Uso': freq,
        'Interacciones_30d': inter30,
        'Uso_Ultimo_Mes': uso_ult_mes,
        'Churn': churn,
        'Segmento': segmento
    })
    return df


def load_clientes(path: str = None) -> pd.DataFrame:
    """Carga clientes desde `path` (CSV). Si no existe, devuelve un DataFrame de ejemplo.

    El CSV esperado debe tener al menos las columnas:
    ID_Cliente, Nombre, Antigüedad, Valor_Mensual, Última_Interacción, Estado_Actual
    """
    # Si el usuario indica ruta, tomarla; si no, buscar archivos comunes
    candidates = []
    if path:
        p = Path(path)
        if p.exists():
            try:
                df = pd.read_csv(p, parse_dates=['Última_Interacción'], dayfirst=True)
                return df
            except Exception:
                try:
                    df = pd.read_csv(p)
                    return df
                except Exception:
                    pass
    # Buscar archivos comunes
    for p in [Path('clientes.csv'), Path('data/clientes.csv'), Path('data/clientes_export.csv')]:
        if p.exists():
            try:
                df = pd.read_csv(p, parse_dates=['Última_Interacción'], dayfirst=True)
                return df
            except Exception:
                try:
                    df = pd.read_csv(p)
                    return df
                except Exception:
                    pass
    # Si no se encontró CSV, devolvemos ejemplo
    return _sample_dataframe()


def riesgo_simple(row):
    """Heurística ligera para marcar alto riesgo si cumple condiciones simples."""
    try:
        if row.get('Churn', 0) == 1:
            return True
        if row.get('Antigüedad', 999) < 6 and row.get('Interacciones_30d', 0) <= 1:
            return True
        if row.get('Uso_Ultimo_Mes', 1.0) < 0.2 and row.get('Interacciones_30d', 0) < 3:
            return True
    except Exception:
        return False
    return False
# data_loader.py - Carga y limpieza de datos

import pandas as pd

def load_clientes(path='clientes.csv'):
    """Carga clientes desde CSV o SQL (ajustar según necesidad)"""
    df = pd.read_csv(path)
    # Limpieza básica
    df['Antigüedad'] = df['Antigüedad'].fillna(0).astype(int)
    df['Valor_Mensual'] = df['Valor_Mensual'].fillna(0)
    df['Última_Interacción'] = pd.to_datetime(df['Última_Interacción'])
    df['Estado_Actual'] = df['Estado_Actual'].fillna('Inactivo')
    return df

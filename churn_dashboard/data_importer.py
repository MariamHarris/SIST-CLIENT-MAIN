"""Módulo para importar clientes desde CSV/Excel, validar columnas y guardar en SQLite."""
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, DateTime, MetaData
import os

REQUIRED_COLS = [
    'ID_Cliente', 'Nombre', 'Antigüedad', 'Valor_Mensual', 'Última_Interacción', 'Estado_Actual'
]

def importar_archivo():
    """UI para importar archivo y validación básica."""
    st.subheader('Importar clientes desde archivo')
    file = st.file_uploader('Selecciona un archivo CSV o Excel', type=['csv', 'xlsx'])
    if not file:
        return None
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as e:
        st.error(f'Error al leer archivo: {e}')
        return None
    # Validar columnas
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f'Faltan columnas requeridas: {missing}')
        return None
    st.success('Archivo cargado y validado correctamente.')
    st.dataframe(df.head())
    if st.button('Guardar en base de datos'):
        ok = guardar_en_sqlite(df)
        if ok:
            st.success('Datos guardados en la base de datos.')
        else:
            st.error('Error al guardar en la base de datos.')
    return df

def guardar_en_sqlite(df, db_path='clientes_importados.sqlite'):
    """Guarda el DataFrame en una tabla 'clientes' en SQLite."""
    try:
        engine = create_engine(f'sqlite:///{db_path}')
        df.to_sql('clientes', engine, if_exists='replace', index=False)
        return True
    except Exception as e:
        print('Error al guardar en BD:', e)
        return False
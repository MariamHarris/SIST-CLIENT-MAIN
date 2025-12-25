import streamlit as st
import pandas as pd
from math import ceil
from churn_dashboard.data_loader import riesgo_simple


def mostrar_tabla(df: pd.DataFrame, page_size=20):
    """Muestra una tabla interactiva con filtros, ordenamiento y paginación simple.

    Columnas mostradas: ID_Cliente, Nombre, Antigüedad, Valor_Mensual, Última_Interacción, Estado_Actual
    Añade badge visual para alto riesgo usando `riesgo_simple`.
    """
    cols = ['ID_Cliente', 'Nombre', 'Antigüedad', 'Valor_Mensual', 'Última_Interacción', 'Estado_Actual']
    available = [c for c in cols if c in df.columns]

    st.sidebar.subheader('Filtros Tabla')
    # Rangos
    if 'Antigüedad' in df.columns:
        min_a, max_a = int(df['Antigüedad'].min()), int(df['Antigüedad'].max())
        rango_a = st.sidebar.slider('Antigüedad (meses)', min_value=min_a, max_value=max_a, value=(min_a, max_a))
        df = df[(df['Antigüedad'] >= rango_a[0]) & (df['Antigüedad'] <= rango_a[1])]
    if 'Valor_Mensual' in df.columns:
        min_v, max_v = float(df['Valor_Mensual'].min()), float(df['Valor_Mensual'].max())
        rango_v = st.sidebar.slider('Valor mensual', min_value=float(min_v), max_value=float(max_v), value=(float(min_v), float(max_v)))
        df = df[(df['Valor_Mensual'] >= rango_v[0]) & (df['Valor_Mensual'] <= rango_v[1])]

    q = st.sidebar.text_input('Buscar por nombre')
    if q:
        df = df[df['Nombre'].str.contains(q, case=False, na=False)]

    # Ordenamiento
    sort_col = st.selectbox('Ordenar por', options=available, index=0) if available else None
    if sort_col:
        df = df.sort_values(by=sort_col)

    # Paginar
    total = len(df)
    pages = ceil(total / page_size) if page_size else 1
    page = st.number_input('Página', min_value=1, max_value=max(1, pages), value=1)
    start = (page-1) * page_size
    end = start + page_size
    display_df = df.iloc[start:end].copy()

    # Badge para alto riesgo
    if 'Probabilidad_Churn' not in display_df.columns:
        display_df['Alto_Riesgo'] = display_df.apply(lambda r: 'ALTO' if riesgo_simple(r) else '', axis=1)
    else:
        display_df['Alto_Riesgo'] = display_df['Probabilidad_Churn'].apply(lambda p: 'ALTO' if p>=50 else '')

    # Mostrar tabla
    st.write(f'Mostrando {start+1}-{min(end,total)} de {total} registros')
    st.dataframe(display_df[available + ['Alto_Riesgo']])
# datagrid.py - Tabla interactiva de clientes

import streamlit as st
import pandas as pd

def mostrar_tabla(df):
    nombre = st.text_input("Buscar por nombre")
    ant_min, ant_max = st.slider("Antigüedad (meses)", 0, int(df['Antigüedad'].max()), (0, int(df['Antigüedad'].max())))
    val_min, val_max = st.slider("Valor mensual", 0, int(df['Valor_Mensual'].max()), (0, int(df['Valor_Mensual'].max())))
    df_filtrado = df[
        df['Antigüedad'].between(ant_min, ant_max) &
        df['Valor_Mensual'].between(val_min, val_max)
    ]
    if nombre:
        df_filtrado = df_filtrado[df_filtrado['Nombre'].str.contains(nombre, case=False)]
    sort_col = st.selectbox("Ordenar por", df.columns, index=0)
    asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"
    df_filtrado = df_filtrado.sort_values(sort_col, ascending=asc)
    def badge_riesgo(row):
        if 'Riesgo' in row and row['Riesgo'] == 'Alto':
            return f"🛑 {row['Riesgo']}"
        return row.get('Riesgo', '')
    if 'Riesgo' in df_filtrado.columns:
        df_filtrado['Riesgo'] = df_filtrado.apply(badge_riesgo, axis=1)
    st.dataframe(df_filtrado[['ID_Cliente', 'Nombre', 'Antigüedad', 'Valor_Mensual', 'Última_Interacción', 'Estado_Actual', 'Riesgo']].head(20), use_container_width=True)
    st.caption("Mostrando primeros 20 registros. Usa filtros para refinar.")

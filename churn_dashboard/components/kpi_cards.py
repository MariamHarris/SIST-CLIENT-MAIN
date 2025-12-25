import streamlit as st
import pandas as pd


def mostrar_kpis(df: pd.DataFrame):
    """Muestra KPI cards en la parte superior del dashboard."""
    total = len(df)
    activos = int((df['Estado_Actual'] == 'Activo').sum()) if 'Estado_Actual' in df.columns else total
    inactivos = total - activos
    tasa_churn = None
    if 'Churn' in df.columns:
        tasa_churn = float(df['Churn'].mean() * 100)

    valor_prom = float(df['Valor_Mensual'].mean()) if 'Valor_Mensual' in df.columns else None
    antig_prom = float(df['Antigüedad'].mean()) if 'Antigüedad' in df.columns else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Clientes Activos', f"{activos}", delta=f"-{inactivos} inactivos")
    c2.metric('Tasa promedio de churn', f"{tasa_churn:.2f}%" if tasa_churn is not None else 'N/A')
    c3.metric('Valor mensual promedio', f"${valor_prom:,.2f}" if valor_prom is not None else 'N/A')
    c4.metric('Antigüedad promedio (meses)', f"{antig_prom:.1f}" if antig_prom is not None else 'N/A')
# kpi_cards.py - KPIs y resumen estadístico

import streamlit as st

def mostrar_kpis(df):
    total = len(df)
    activos = df[df['Estado_Actual'] == 'Activo'].shape[0]
    inactivos = total - activos
    churn_rate = df['Churn'].mean() * 100 if 'Churn' in df else 0
    valor_prom = df['Valor_Mensual'].mean()
    antig_prom = df['Antigüedad'].mean()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes Activos", activos)
    col2.metric("Clientes Inactivos", inactivos)
    col3.metric("Tasa Churn (%)", f"{churn_rate:.1f}")
    col4.metric("Valor Mensual Prom.", f"${valor_prom:.2f}")
    st.caption(f"Antigüedad promedio: {antig_prom:.1f} meses")

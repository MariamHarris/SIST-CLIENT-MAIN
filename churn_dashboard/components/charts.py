import streamlit as st
import plotly.express as px
import pandas as pd


def histograma_antiguedad(df: pd.DataFrame):
    """Histograma de distribución de antigüedad (meses)."""
    if 'Antigüedad' not in df.columns:
        st.info('No hay datos de antigüedad')
        return
    fig = px.histogram(df, x='Antigüedad', nbins=20, title='Distribución de antigüedad (meses)')
    st.plotly_chart(fig, use_container_width=True)


def pie_segmento(df: pd.DataFrame):
    """Gráfico circular por `Segmento` (si existe)."""
    if 'Segmento' not in df.columns:
        st.info('No hay datos de segmento')
        return
    s = df['Segmento'].value_counts().reset_index()
    s.columns = ['Segmento', 'Cantidad']
    fig = px.pie(s, names='Segmento', values='Cantidad', title='Distribución por segmento')
    st.plotly_chart(fig, use_container_width=True)
# charts.py - Gráficos

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def histograma_antiguedad(df):
    fig = px.histogram(df, x='Antigüedad', nbins=20, title="Distribución de Antigüedad")
    st.plotly_chart(fig, use_container_width=True)

def pie_segmento(df):
    if 'Segmento' in df.columns:
        fig = px.pie(df, names='Segmento', title="Distribución por Segmento")
        st.plotly_chart(fig, use_container_width=True)

def gauge_churn(prob):
    color = "green" if prob < 0.2 else "yellow" if prob < 0.5 else "red"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob*100,
        gauge = {
            'axis': {'range': [0,100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0,20], 'color': 'lightgreen'},
                {'range': [20,50], 'color': 'yellow'},
                {'range': [50,100], 'color': 'red'}
            ]
        },
        title = {'text': "Probabilidad de Churn (%)"}
    ))
    st.plotly_chart(fig, use_container_width=True)

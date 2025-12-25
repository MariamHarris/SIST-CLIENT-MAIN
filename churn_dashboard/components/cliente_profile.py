import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from churn_dashboard.model import predecir_proba, top_features_contrib
from churn_dashboard.logging_utils import log_prediction


def mostrar_perfil_cliente(df: pd.DataFrame, cliente_id, modelo, features):
    """Muestra perfil del cliente, predicción y recomendaciones.

    `cliente_id` puede ser ID_Cliente o Nombre.
    """
    # Buscar cliente
    if cliente_id in df['ID_Cliente'].values:
        row = df[df['ID_Cliente'] == cliente_id].iloc[0]
    else:
        matches = df[df['Nombre'].str.contains(str(cliente_id), case=False, na=False)]
        if matches.empty:
            st.warning('Cliente no encontrado')
            return
        row = matches.iloc[0]

    st.subheader(f"Perfil: {row.get('Nombre')} ({row.get('ID_Cliente')})")
    st.write('Antigüedad (meses):', row.get('Antigüedad'))
    st.write('Valor mensual:', row.get('Valor_Mensual'))
    st.write('Última interacción:', row.get('Última_Interacción'))

    # Preparar input para modelo
    X_row = pd.DataFrame([row[features].to_dict()])
    proba = None
    try:
        proba = predecir_proba(modelo, X_row)[0]
    except Exception as e:
        st.warning('No se pudo calcular probabilidad: ' + str(e))

    # Gauge chart
    if proba is not None:
        color = 'green' if proba < 20 else ('yellow' if proba < 50 else 'red')
        nivel = 'Bajo' if proba < 20 else ('Medio' if proba < 50 else 'Alto')
        fig = go.Figure(go.Indicator(
            mode='gauge+number',
            value=proba,
            title={'text':'Probabilidad de churn (%)'},
            gauge={'axis': {'range':[0,100]}, 'bar': {'color': color}}
        ))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Nivel de riesgo:** {nivel}")

        # Factores clave (top features globales)
        top = top_features_contrib(modelo, X_row, features, top_n=5)
        if top:
            st.subheader('Factores de influencia')
            for i, (k,v) in enumerate(top, start=1):
                st.write(f"{i}. {k} (importancia: {v:.3f})")

        # Recomendaciones simples
        st.subheader('Recomendaciones')
        recs = []
        if proba >= 50:
            recs.append('Contacto urgente: llamar en 48 horas y ofrecer retención')
            recs.append('Descuento o paquete personalizado por 3 meses')
        elif proba >= 20:
            recs.append('Enviar email personalizado con beneficios')
            recs.append('Monitorear uso en próximas 2 semanas')
        else:
            recs.append('Segmentar para campañas de upsell')

        for r in recs:
            st.write('- ' + r)

        # Log de la predicción
        try:
            log_prediction(cliente_id=row.get('ID_Cliente'), prob=proba, nivel=nivel, factores=[k for k,_ in top])
        except Exception:
            pass
# cliente_profile.py - Página de predicción por cliente

import streamlit as st
from .charts import gauge_churn
from model import predecir_cliente

def mostrar_perfil_cliente(df, cliente_id, modelo, features):
    cliente = df[df['ID_Cliente'] == cliente_id].iloc[0]
    st.subheader(f"Perfil de {cliente['Nombre']}")
    st.write(f"Antigüedad: {cliente['Antigüedad']} meses")
    st.write(f"Valor mensual: ${cliente['Valor_Mensual']:.2f}")
    st.write(f"Última interacción: {cliente['Última_Interacción']}")
    st.write(f"Estado actual: {cliente['Estado_Actual']}")
    proba, pred = predecir_cliente(modelo, cliente.to_frame().T, features)
    gauge_churn(proba)
    nivel = "Bajo" if proba < 0.2 else "Medio" if proba < 0.5 else "Alto"
    st.markdown(f"**Nivel de riesgo:** :{'green' if nivel=='Bajo' else 'yellow' if nivel=='Medio' else 'red'}[{nivel}]")
    st.markdown("**Factores clave:**")
    st.write("- Disminución del 40% en uso último mes")
    st.write("- Sin interacción en 21 días")
    st.write("- Antigüedad < 6 meses")
    st.markdown("**Recomendaciones:**")
    st.write("• Contactar en próxima semana")
    st.write("• Oferta de retención personalizada")

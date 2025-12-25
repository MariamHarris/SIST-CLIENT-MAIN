import os, sys
from datetime import datetime
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sist_pred_client.settings")

import django
django.setup()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Intenta importar el modelo Cliente; si no existe, usa datos de ejemplo
try:
    from clientes.models import Cliente
except Exception:
    Cliente = None

st.set_page_config(page_title="Churn Dashboard", layout="wide")

# Campos esperados (ajusta si necesario)
AGE_FIELD = "edad"
INCOME_FIELD = "ingresos"
DATE_FIELD = "fecha_alta"
STATUS_FIELD = "estado"
PROB_FIELD = "churn_prob"

@st.cache_data(ttl=60)
def load_data():
    if Cliente:
        qs = Cliente.objects.all()
        rows = []
        for c in qs:
            rows.append({
                "id": c.id,
                "nombre": getattr(c, "nombre", str(c)),
                "edad": getattr(c, AGE_FIELD, None),
                "ingresos": getattr(c, INCOME_FIELD, None),
                "fecha_alta": getattr(c, DATE_FIELD, None),
                "estado": getattr(c, STATUS_FIELD, "").lower(),
                "churn_prob": getattr(c, PROB_FIELD, None),
            })
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame([
            {"id":1,"nombre":"Acme","edad":34,"ingresos":45000,"fecha_alta":datetime(2020,5,1),"estado":"activo","churn_prob":0.12},
            {"id":2,"nombre":"Beta","edad":52,"ingresos":70000,"fecha_alta":datetime(2019,2,10),"estado":"inactivo","churn_prob":0.78},
            {"id":3,"nombre":"Gamma","edad":28,"ingresos":22000,"fecha_alta":datetime(2021,8,15),"estado":"activo","churn_prob":0.35},
        ])
    # fallback churn_prob heurístico
    if "churn_prob" not in df.columns or df["churn_prob"].isnull().all():
        df["churn_prob"] = df.apply(lambda r: min(0.95, ((int(r.get("id",0))%10) + len(str(r.get("nombre","")))) / 100), axis=1)
    if DATE_FIELD in df.columns:
        df["fecha_alta"] = pd.to_datetime(df["fecha_alta"], errors="coerce")
    return df

df = load_data()

st.title("Dashboard — Churn Prediction")

with st.sidebar:
    st.header("Filtros")
    min_date = df["fecha_alta"].min() if "fecha_alta" in df.columns else None
    max_date = df["fecha_alta"].max() if "fecha_alta" in df.columns else None
    date_range = None
    if pd.notnull(min_date) and pd.notnull(max_date):
        date_range = st.date_input("Rango fecha alta", value=(min_date.date(), max_date.date()))
    estados = df["estado"].dropna().unique().tolist() if "estado" in df.columns else []
    estado_sel = st.multiselect("Estado", options=estados, default=estados or None)
    min_risk, max_risk = st.slider("Rango probabilidad (%)", 0, 100, (0, 100))
    st.markdown("---")
    st.write("Export:")
    st.info("CSV / PNG desde botones en la UI")

# Aplicar filtros
df_filtered = df.copy()
if date_range:
    start, end = [pd.to_datetime(d) for d in date_range]
    df_filtered = df_filtered[(df_filtered["fecha_alta"] >= start) & (df_filtered["fecha_alta"] <= end + pd.Timedelta(days=1))]
if estado_sel:
    df_filtered = df_filtered[df_filtered["estado"].isin([e.lower() for e in estado_sel])]
df_filtered = df_filtered[(df_filtered["churn_prob"]*100 >= min_risk) & (df_filtered["churn_prob"]*100 <= max_risk)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Clientes (filtrados)", len(df_filtered))
col2.metric("Churn promedio", f"{(df_filtered['churn_prob'].mean()*100 if len(df_filtered) else 0):.2f}%")
col3.metric("Alto riesgo (>80%)", int((df_filtered['churn_prob'] > 0.8).sum()))
col4.metric("Última actualización", datetime.now().strftime("%Y-%m-%d %H:%M"))

# Charts
left, right = st.columns([2,1])

with left:
    st.subheader("Distribución de riesgo")
    fig_dist = px.histogram(df_filtered, x="churn_prob", nbins=40, labels={"churn_prob":"Probabilidad"}, title="Distribución de probabilidad de churn")
    fig_dist.update_traces(marker_color='indianred')
    st.plotly_chart(fig_dist, use_container_width=True)

    st.subheader("Histogramas demográficos")
    demo_tab = st.tabs(["Edad", "Ingresos", "Antigüedad"])
    with demo_tab[0]:
        if "edad" in df_filtered.columns and df_filtered["edad"].notnull().any():
            fig_age = px.histogram(df_filtered, x="edad", nbins=20, title="Distribución por edad")
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("Campo 'edad' no disponible")
    with demo_tab[1]:
        if "ingresos" in df_filtered.columns and df_filtered["ingresos"].notnull().any():
            fig_inc = px.histogram(df_filtered, x="ingresos", nbins=25, title="Distribución por ingresos")
            st.plotly_chart(fig_inc, use_container_width=True)
        else:
            st.info("Campo 'ingresos' no disponible")
    with demo_tab[2]:
        if "fecha_alta" in df_filtered.columns and df_filtered["fecha_alta"].notnull().any():
            df_filtered["antiguedad_days"] = (pd.Timestamp.now() - df_filtered["fecha_alta"]).dt.days
            fig_ten = px.histogram(df_filtered, x="antiguedad_days", nbins=30, title="Antigüedad (días)")
            st.plotly_chart(fig_ten, use_container_width=True)
        else:
            st.info("Campo 'fecha_alta' no disponible")

with right:
    st.subheader("Activo vs Inactivo")
    if "estado" in df_filtered.columns and df_filtered["estado"].notnull().any():
        counts = df_filtered["estado"].value_counts().reset_index()
        counts.columns = ["estado","count"]
        fig_status = px.pie(counts, values="count", names="estado", title="Activo vs Inactivo")
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("Campo 'estado' no disponible")

    st.subheader("Segmentación por riesgo")
    def risk_label(p):
        p100 = p*100
        if p100 < 30: return "Bajo"
        if p100 < 70: return "Medio"
        return "Alto"
    df_filtered["risk_label"] = df_filtered["churn_prob"].apply(risk_label)
    seg_counts = df_filtered["risk_label"].value_counts().reindex(["Alto","Medio","Bajo"]).fillna(0)
    fig_seg = px.bar(x=seg_counts.index, y=seg_counts.values, labels={"x":"Segmento","y":"Clientes"}, title="Clientes por segmento de riesgo")
    st.plotly_chart(fig_seg, use_container_width=True)

    numeric_cols = df_filtered.select_dtypes(include="number").columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ("id","churn_prob","antiguedad_days")]
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X axis", options=numeric_cols, index=0)
        y_col = st.selectbox("Y axis", options=numeric_cols, index=1)
        fig_scatter = px.scatter(df_filtered, x=x_col, y=y_col, color="risk_label", hover_data=["nombre","churn_prob"], title="Segmentación (scatter)")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No hay suficientes columnas numéricas para scatter")

st.subheader("Tabla de clientes filtrados")
st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)

csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Descargar CSV (filtrado)", data=csv_bytes, file_name="clientes_filtrados.csv", mime="text/csv")

if st.button("Exportar Distribución como PNG"):
    try:
        img_bytes = pio.to_image(fig_dist, format="png", width=1200, height=600, engine="kaleido")
        st.download_button("Descargar PNG", data=img_bytes, file_name="distribucion_churn.png", mime="image/png")
    except Exception as e:
        st.error("Fallo al generar PNG. Instala 'kaleido' y prueba de nuevo: pip install kaleido")

st.sidebar.markdown("---")
st.sidebar.markdown("Notas: Streamlit para prototipo; embed en Django via iframe o usar django-plotly-dash para integración profunda.")

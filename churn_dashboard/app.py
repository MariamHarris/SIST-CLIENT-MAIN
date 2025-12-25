
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from data_loader import load_clientes
from data_importer import importar_archivo
from model import entrenar_modelo, guardar_modelo, cargar_modelo
from components.kpi_cards import mostrar_kpis
from components.datagrid import mostrar_tabla
from components.charts import histograma_antiguedad, pie_segmento
from components.cliente_profile import mostrar_perfil_cliente

# --- Autenticación y roles ---
users = [
	{"name": "Admin", "username": "admin", "password": stauth.Hasher(["admin123"]).generate()[0], "role": "admin"},
	{"name": "Analista", "username": "analista", "password": stauth.Hasher(["analista123"]).generate()[0], "role": "analista"}
]
usernames = [u["username"] for u in users]
names = [u["name"] for u in users]
hashed_pw = [u["password"] for u in users]
roles = {u["username"]: u["role"] for u in users}

authenticator = stauth.Authenticate(names, usernames, hashed_pw, "churn_dashboard", "abcdef", cookie_expiry_days=1)
name, auth_status, username = authenticator.login("Iniciar sesión", "main")

if auth_status is False:
	st.error("Usuario o contraseña incorrectos")
	st.stop()
elif auth_status is None:
	st.warning("Por favor, ingresa tus credenciales")
	st.stop()

rol = roles.get(username, "analista")
st.sidebar.info(f"Usuario: {name} | Rol: {rol}")
if st.sidebar.button("Cerrar sesión"):
	authenticator.logout("Cerrar sesión", "sidebar")
	st.stop()

st.set_page_config(page_title="Panel Churn", layout="wide")
st.sidebar.title("Navegación")

# Definir páginas según rol
paginas = ["Dashboard", "Clientes", "Predicción por cliente"]
if rol == "admin":
	paginas.insert(2, "Entrenamiento")
	paginas.append("Importar clientes")
page = st.sidebar.radio("Ir a:", paginas)
if page == "Importar clientes":
	if rol != "admin":
		st.error("Acceso restringido: solo administradores pueden importar datos.")
	else:
		importar_archivo()

df = load_clientes()

if page == "Dashboard":
	st.title("Resumen de Clientes")
	mostrar_kpis(df)
	col1, col2 = st.columns(2)
	with col1:
		histograma_antiguedad(df)
	with col2:
		pie_segmento(df)

elif page == "Clientes":
	st.title("Gestión de Clientes")
	mostrar_tabla(df)


if page == "Entrenamiento":
	if rol != "admin":
		st.error("Acceso restringido: solo administradores pueden entrenar el modelo.")
	else:
		st.title("Entrenamiento del Modelo")
		features = ['Antigüedad', 'Valor_Mensual']  # Ajustar según dataset real
		target = 'Churn'
		if st.button("Entrenar Modelo"):
			with st.spinner("Entrenando..."):
				modelo, metrics = entrenar_modelo(df, features, target)
				guardar_modelo(modelo)
			st.success("Modelo entrenado y guardado.")
			st.write("Matriz de confusión:")
			st.write(metrics['confusion_matrix'])
			st.write("Reporte:")
			st.json(metrics['classification_report'])
			st.write(f"ROC AUC: {metrics['roc_auc']:.3f}")
			# Importancia de variables
			if metrics['feature_importances'] is not None:
				st.subheader("Importancia de variables")
				st.bar_chart(metrics['feature_importances'])
		else:
			st.info("Haz clic en 'Entrenar Modelo' para iniciar.")

elif page == "Predicción por cliente":
	st.title("Predicción Individual")
	try:
		modelo = cargar_modelo()
		cliente_id = st.selectbox("Selecciona cliente", df['ID_Cliente'])
		mostrar_perfil_cliente(df, cliente_id, modelo, ['Antigüedad', 'Valor_Mensual'])
	except Exception as e:
		st.warning("Primero debes entrenar y guardar el modelo.")

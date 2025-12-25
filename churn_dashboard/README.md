# Dashboard de Churn y Gestión de Clientes

## Descripción
Panel analítico en Streamlit para gestión de clientes y predicción de abandono (churn), con entrenamiento de modelo, visualización de KPIs, tabla interactiva, predicción individual y logging de resultados.

## Requisitos
- Python 3.8+
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución
Desde la raíz del proyecto:

```bash
streamlit run churn_dashboard/app.py
```

## Funcionalidades
- **Dashboard:** KPIs, histograma de antigüedad, pie por segmento.
- **Clientes:** Tabla interactiva con filtros, búsqueda, paginación y badge de alto riesgo.
- **Entrenamiento:** Entrena modelo RandomForest, muestra métricas y permite guardar modelo.
- **Predicción por cliente:** Selección, gauge de probabilidad, factores clave y recomendaciones.
- **Logging:** Cada predicción se registra en `predictions_log.csv`.

## Personalización
- Para usar tus propios datos, coloca un CSV con las columnas requeridas en la raíz o en `data/`.
- Para integración SQL, adapta `load_clientes()` en `data_loader.py`.

## Sugerencias de mejora
- Integrar SHAP para explicaciones locales.
- Añadir autenticación y control de acceso.
- Conexión directa a base de datos SQL.

## Comentarios
- Todo el código y la UI están en español.
- Preparado para producción y fácil integración con Django/SQL.# Panel de Gestión de Clientes y Churn

Este proyecto implementa un dashboard analítico para gestión de clientes y predicción de abandono (churn) usando Streamlit, Scikit-learn y Plotly.

## Estructura
- `app.py`: Entrada principal
- `data_loader.py`: Carga de datos
- `model.py`: ML y predicción
- `components/`: Componentes visuales

## Instalación
```bash
pip install -r requirements.txt
```

## Ejecución
```bash
streamlit run app.py
```

## Notas
- Preparado para integración SQL/CSV
- Código y comentarios en español

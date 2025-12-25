# Snippet: crear app Dash embebible en Django templates
# Requiere: pip install django-plotly-dash dash plotly
from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

app = DjangoDash("ChurnDash")  # name used in template {% plotly_app name="ChurnDash" %}
# ejemplo de figura estática; genera datos desde tu ORM similar al Streamlit app
fig = px.histogram([0.1,0.5,0.2,0.8], nbins=10, title="Distribución de riesgo (ejemplo)")

app.layout = html.Div([
    html.H3("Dashboard Churn (Dash)"),
    dcc.Graph(figure=fig),
])
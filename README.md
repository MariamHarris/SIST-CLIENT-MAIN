# Requisitos
- Python 3.x (recomendado 3.11+)

# Instalación (Windows)
1) Clonar el repo
2) Crear y activar entorno virtual
	- `python -m venv venv`
	- `venv\Scripts\Activate.ps1`
3) Instalar dependencias
	- `pip install -r requirements.txt`
4) Configurar base de datos
	- `python manage.py migrate`
5) (Opcional) Crear superusuario
	- `python manage.py createsuperuser`

# Variables de entorno (recomendado)
- Copia `.env.example` a `.env` y ajusta valores.
- Variables soportadas:
  - `DJANGO_DEBUG`
  - `DJANGO_SECRET_KEY`
  - `DJANGO_ALLOWED_HOSTS` (separado por comas)
  - `DJANGO_CSRF_TRUSTED_ORIGINS` (separado por comas)

# Levantar el servidor
- Local:
  - `python manage.py runserver`

- Si el proyecto está en OneDrive y ves errores raros del auto-reload, usa:
  - `python manage.py runserver --noreload`

# Flujo recomendado (MUST HAVE)
1) Importar clientes
  - Menú: Clientes → Importar
  - Formatos: CSV o Excel
2) Entrenar el modelo (solo admin)
  - Menú: Predicciones → botón "Entrenar modelo"
  - Nota: para entrenar, deben existir clientes con `estado=inactivo` (si no, el endpoint avisa).
3) Predecir por cliente
  - Menú: Predicciones → botón "Predecir" en la fila del cliente
  - Resultado: muestra probabilidad (%) y nivel (Bajo/Medio/Alto) y lo guarda en el cliente.

# Resumen estadístico (JSON)
- Endpoint: `/dashboard/api/stats/`
- Devuelve (ejemplo): total de clientes, distribución por riesgo/estado y probabilidad promedio.

- En red (para acceder desde otra PC en la misma LAN):
  1) `python manage.py runserver 0.0.0.0:8000`
  2) En tu `.env`, agrega el IP del servidor a `DJANGO_ALLOWED_HOSTS`
	  - Ejemplo: `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50`

git clone https://github.com/02yari/sist-client.git
Crear entorno virtual: python -m venv venv, venv\Scripts\activate
Instalar dependencias: pip install -r requirements.txt
Configurar base de dato: python manage.py migrate
crear super usuario: python manage.py createsuperuser
Servidor: python manage.py runserver

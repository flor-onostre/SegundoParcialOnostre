# SegundoParcialOnostre (Django)

Proyecto Django para el segundo parcial de Programación IV. Incluye registro/login, dashboard de alumnos con PDF por email, scraping educativo (Wikipedia) y envío de resultados por correo usando la API de Brevo.

[Deployment en Render](https://segundoparcialonostre.onrender.com)

## Requisitos
- Python 3.10+
- pip
- Virtualenv (recomendado)

## Instalación y ejecución local
```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell: .\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Variables de entorno (.env)
Coloca un archivo `.env` en la raíz (junto a `manage.py`). Ejemplo:
```
DJANGO_SECRET_KEY=tu_clave_segura
DJANGO_DEBUG=True

BREVO_API_KEY=tu_api_key
BREVO_SENDER_EMAIL=tu_correo@ejemplo.com
BREVO_SENDER_NAME=SegundoParcialOnostre
```
Brevo se usa para todos los correos (bienvenida, PDF de alumno, resultados de scraper). El backend de Django está desactivado para SMTP/console.

### Postgres en Render
Define `DATABASE_URL` (Render la expone al crear la BD). El proyecto detecta esa variable y usa Postgres con `dj-database-url` y `psycopg2-binary`; si no está, usa SQLite local.

## Funcionalidades
- **Autenticación**: registro, login/logout, reset de contraseña (todo con Brevo).
- **Dashboard de alumnos**: crea/lista/elimina alumnos por usuario. Genera y envía PDF (ReportLab) al correo del usuario.
- **Scraper educativo**: busca en Wikipedia (es), muestra resultados en tabla y permite enviarlos por correo en tabla HTML.
- **UI**: Bootstrap 5, navbar con acceso a Alumnos y Scraper, footer con datos del parcial.

## Deploy (Render/Heroku-like)
- Usa `Procfile` con `web: gunicorn SegundoParcialOnostre.wsgi`.
- Ajusta variables de entorno en el panel (las mismas del `.env`).
- Ejecuta en build/release: `python manage.py collectstatic --noinput` y `python manage.py migrate`.

## Estructura
- `manage.py`
- `SegundoParcialOnostre/` (settings, urls, email_utils, wsgi/asgi)
- `accounts/`, `alumnos/`, `scraper/` (apps)
- `templates/`, `static/`

## Notas
- El envío de correos depende de Brevo: si falla, revisa las variables y la consola del server para ver el error de la API.
- Base de datos por defecto: SQLite (`db.sqlite3`). Cambia `DATABASES` en `settings.py` si necesitas otro motor. 

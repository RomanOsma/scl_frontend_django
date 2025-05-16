# scl_frontend_django/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env' # Para desarrollo local
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"INFO: Archivo .env cargado desde: {dotenv_path}")

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'una_clave_secreta_de_fallback_solo_para_desarrollo_local_cambiar_en_produccion')
DEBUG_ENV_VALUE = os.getenv('DJANGO_DEBUG', 'False').lower() # Por defecto False para producción
DEBUG = DEBUG_ENV_VALUE in ['true', '1', 't', 'yes']

ALLOWED_HOSTS_STRING = os.getenv('DJANGO_ALLOWED_HOSTS')
if ALLOWED_HOSTS_STRING:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',')]
elif DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
else: # DEBUG es False y no hay variable de entorno
    ALLOWED_HOSTS = [] # Esto fallará en producción si no se setea la variable, lo cual es bueno.

print(f"INFO (settings.py): DEBUG = {DEBUG}")
print(f"INFO (settings.py): ALLOWED_HOSTS = {ALLOWED_HOSTS}")

# Reemplaza esto con tu dominio real de Railway para el frontend
PUBLIC_RAILWAY_FRONTEND_DOMAIN = 'sclfrontenddjango-production.up.railway.app' 

CSRF_TRUSTED_ORIGINS_ENV = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = [f"https://{PUBLIC_RAILWAY_FRONTEND_DOMAIN}"]
    if DEBUG: # Para desarrollo local, añade http y localhost si es necesario
        CSRF_TRUSTED_ORIGINS.extend([f"http://{PUBLIC_RAILWAY_FRONTEND_DOMAIN}", 'http://127.0.0.1:8001', 'http://localhost:8001'])

print(f"INFO (settings.py): CSRF_TRUSTED_ORIGINS = {CSRF_TRUSTED_ORIGINS}")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    print("INFO (settings.py): Configuraciones SECURE_* para producción aplicadas.")

INSTALLED_APPS = [
    'portal.apps.PortalConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para servir estáticos con runserver si DEBUG=False
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
FASTAPI_BASE_URL = os.getenv('FASTAPI_BASE_URL', 'http://127.0.0.1:8000/api/v1')
# print(f"INFO (settings.py): FASTAPI_BASE_URL = {FASTAPI_BASE_URL}")
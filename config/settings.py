# scl_frontend_django/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"INFO: Archivo .env cargado desde: {dotenv_path}")
else:
    print(f"ADVERTENCIA: No se encontró .env en {dotenv_path} (esperado en producción si las variables están en el entorno de Railway).")

# SECRET_KEY - Lee de DJANGO_SECRET_KEY
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY', 
    'django-insecure-fallback-key-for-dev-if-not-in-env-CHANGE-ME' 
)
if SECRET_KEY == 'django-insecure-fallback-key-for-dev-if-not-in-env-CHANGE-ME':
    print("ADVERTENCIA: Usando SECRET_KEY de fallback. ¡Configúrala en .env o variables de entorno de producción!")

# DEBUG - Lee de DJANGO_DEBUG
DEBUG_ENV_VALUE = os.getenv('DJANGO_DEBUG', 'False').lower() # Por defecto 'False' si no está definida
DEBUG = DEBUG_ENV_VALUE in ['true', '1', 't', 'yes']

if DEBUG:
    print("INFO (settings.py): DEBUG está ACTIVADO.")
else:
    print("INFO (settings.py): DEBUG está DESACTIVADO (producción).")

# ALLOWED_HOSTS - Lee de DJANGO_ALLOWED_HOSTS
ALLOWED_HOSTS_STRING = os.getenv('DJANGO_ALLOWED_HOSTS')
if ALLOWED_HOSTS_STRING:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',')]
else:
    if DEBUG: # Si DJANGO_ALLOWED_HOSTS no está, pero DEBUG es True (localmente)
        ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    else: # Si DJANGO_ALLOWED_HOSTS no está y DEBUG es False (producción)
        ALLOWED_HOSTS = [] # Esto causará error si no se configura en Railway, lo cual es bueno

print(f"INFO (settings.py): ALLOWED_HOSTS = {ALLOWED_HOSTS}")

# CSRF_TRUSTED_ORIGINS - Lee de DJANGO_CSRF_TRUSTED_ORIGINS
# Reemplaza 'tu-dominio-frontend.up.railway.app' con tu dominio real de Railway para el frontend
DEFAULT_RAILWAY_FRONTEND_DOMAIN = 'sclfrontenddjango-production.up.railway.app' 

CSRF_TRUSTED_ORIGINS_STRING = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS')
if CSRF_TRUSTED_ORIGINS_STRING:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STRING.split(',')]
else:
    # Valores por defecto si la variable de entorno no está
    CSRF_TRUSTED_ORIGINS = [f"https://{DEFAULT_RAILWAY_FRONTEND_DOMAIN}"] # Para producción
    if DEBUG: # Para desarrollo local, añadir http y localhost
        CSRF_TRUSTED_ORIGINS.extend(['http://127.0.0.1:8001', 'http://localhost:8001'])
        # No necesitas añadir el de Railway con http si DEBUG=True, ya que no estarás accediendo a él así

print(f"INFO (settings.py): CSRF_TRUSTED_ORIGINS = {CSRF_TRUSTED_ORIGINS}")

# Configuraciones SECURE_* (solo si no estás en DEBUG)
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
    'whitenoise.runserver_nostatic', # Útil para probar estáticos con runserver y DEBUG=False
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
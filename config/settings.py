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
    print(f"INFO: No se encontró el archivo .env en {dotenv_path}")

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY_LOCAL', 'fallback_secret_key_de_desarrollo_muy_simple')
DEBUG = os.getenv('DJANGO_DEBUG_LOCAL', 'False').lower() in ['true', '1', 't', 'yes']
ALLOWED_HOSTS_STRING = os.getenv('DJANGO_ALLOWED_HOSTS_LOCAL')
if ALLOWED_HOSTS_STRING:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',')]
elif DEBUG: 
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
else: 
    ALLOWED_HOSTS = [] 

print(f"INFO: DEBUG = {DEBUG}")
print(f"INFO: ALLOWED_HOSTS = {ALLOWED_HOSTS}")

INSTALLED_APPS = [
    'portal.apps.PortalConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
FASTAPI_BASE_URL = os.getenv('FASTAPI_BASE_URL', 'http://127.0.0.1:8000/api/v1')
print(f"INFO: FASTAPI_BASE_URL en settings: {FASTAPI_BASE_URL}")
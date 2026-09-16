"""
Django settings for stockflow project.
Configured for local dev (SQLite) and Railway deployment (Postgres via DATABASE_URL).
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core security settings, driven by environment variables ---------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-change-me-480oaa gdyo6os3ff9ocpskwc4l0vd6pt0wj_u3as1s',
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Railway injects RAILWAY_PUBLIC_DOMAIN / RAILWAY_STATIC_URL; also allow an
# explicit ALLOWED_HOSTS env var (comma-separated) for any other host.
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()
]
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)
# Fallback so a fresh Railway deploy never 400s before ALLOWED_HOSTS is set.
if os.environ.get('RAILWAY_ENVIRONMENT'):
    ALLOWED_HOSTS.append('.up.railway.app')

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]
if railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')
if os.environ.get('RAILWAY_ENVIRONMENT'):
    CSRF_TRUSTED_ORIGINS.append('https://*.up.railway.app')

# --- Applications ------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
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

ROOT_URLCONF = 'stockflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stockflow.wsgi.application'

# --- Database ----------------------------------------------------------------
# Uses SQLite locally by default. On Railway, set DATABASE_URL (Railway does
# this automatically when you attach a Postgres plugin) and it takes over.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# --- Password validation ------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization -----------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static files --------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Security (auto-enabled when DEBUG is off, e.g. on Railway) ---------------
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

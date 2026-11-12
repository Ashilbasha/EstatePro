"""
Django settings for EstatePro.
Supports local MySQL and production PostgreSQL.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url


# ==================================================
# BASE DIRECTORY
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


# ==================================================
# SECURITY SETTINGS
# ==================================================

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY is missing from environment variables"
    )

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'


# ==================================================
# ALLOWED HOSTS
# ==================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]

RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ==================================================
# DEFAULT PRIMARY KEY
# ==================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================================================
# APPLICATION DEFINITION
# ==================================================

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'properties',
    'accounts',

]


# ==================================================
# MIDDLEWARE
# ==================================================

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


# ==================================================
# URL CONFIGURATION
# ==================================================

ROOT_URLCONF = 'config.urls'


# ==================================================
# TEMPLATE CONFIGURATION
# ==================================================

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [],

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


# ==================================================
# WSGI CONFIGURATION
# ==================================================

WSGI_APPLICATION = 'config.wsgi.application'


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:

    # Production: PostgreSQL

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }

else:

    # Local development: MySQL

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'estatepro_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),

            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }


# ==================================================
# PASSWORD VALIDATION
# ==================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },

]


# ==================================================
# INTERNATIONALIZATION
# ==================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# ==================================================
# STATIC FILES
# ==================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {

    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },

    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },

}


# ==================================================
# MEDIA FILES
# ==================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==================================================
# CUSTOMER AUTHENTICATION
# ==================================================

LOGIN_URL = '/accounts/login/'


# ==================================================
# GMAIL SMTP EMAIL CONFIGURATION
# ==================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ==================================================
# BROWSER SECURITY SETTINGS
# ==================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# ==================================================
# SESSION AND CSRF SECURITY
# ==================================================

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SAMESITE = 'Lax'


# ==================================================
# RENDER / PRODUCTION SECURITY
# ==================================================

CSRF_TRUSTED_ORIGINS = [

    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        ''
    ).split(',')
    if origin.strip()

]

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True
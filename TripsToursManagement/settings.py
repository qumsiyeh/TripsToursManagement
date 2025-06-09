# TripsToursManagement/settings.py

from pathlib import Path
import os
import dj_database_url # <--- ADDED: For PostgreSQL database URL parsing
import sys # <--- ADDED: To check if running tests


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable for SECRET_KEY in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-@u1#p5h=p543n(6=v7k$v@g83315a%r48$j275d)w+3j55w!9p')


# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG to False in production. Render automatically sets this to False for production deploys.
# You can override it locally using an env var if needed.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# ALLOWED_HOSTS for Render.com: your Render app's domain and any custom domains
ALLOWED_HOSTS = ['trips-tours-management.onrender.com', 'localhost', '127.0.0.1']
# Add other domains if you set up custom domains on Render
# You can also use ['.onrender.com'] for wildcards, but listing specific domains is safer.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic', # <--- ADDED: For WhiteNoise in development (optional, but good practice)

    # Our custom apps
    'customers',
    'trips',
    'bookings',
    'payments',
    'reports',
    'core',
    'expenses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- ADDED: For serving static files in production
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TripsToursManagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TripsToursManagement.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Use PostgreSQL in production, SQLite for local development (or PostgreSQL locally)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Render automatically sets DATABASE_URL for PostgreSQL
# This parses the DATABASE_URL and uses it if available
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600 # Optional: connection life in seconds
    )

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/topics/static-files/

STATIC_URL = 'static/'
# This tells Django where to look for static files collected from your apps
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# For production deployment, static files will be collected into this directory
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise settings for static files
# Only enable in production. Render automatically sets DJANGO_DEBUG to False for production.
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files (user-uploaded files like customer attachments)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AUTHENTICATION SETTINGS ---
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# For testing database to ensure it's not the production one
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
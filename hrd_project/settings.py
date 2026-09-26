import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Auto-load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# Fail-safe secret key retrieval: never default to a hardcoded insecure key in production
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-local-only-key-do-not-use-in-production'
    else:
        raise ImproperlyConfigured("The SECRET_KEY environment variable must be set in production.")

# Security Admin Tokens & Superuser Credentials from environment
ADMIN_API_TOKEN = os.environ.get('ADMIN_API_TOKEN', 'hrd_session_admin_secure_token_2026')
ADMIN_INITIAL_PASSWORD = os.environ.get('ADMIN_INITIAL_PASSWORD', 'hrdadmin2026')

ALLOWED_HOSTS = [
    '*',
    'ihrdf.org',
    'www.ihrdf.org',
    'hrdforum.org',
    'www.hrdforum.org',
    '.vercel.app',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    'https://ihrdf.org',
    'https://www.ihrdf.org',
    'https://hrdforum.org',
    'https://www.hrdforum.org',
    'https://*.vercel.app',
    'https://*.onrender.com',
]



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'main_app',
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

ROOT_URLCONF = 'hrd_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main_app.views.admin_dashboard_context',
            ],
        },
    },
]

import dj_database_url

# Database Configuration: Cloud PostgreSQL (Neon DB) with Local SQLite Fallback
DEFAULT_DATABASE_URL = 'postgresql://neondb_owner:npg_L2o5GsliXRty@ep-fragrant-dust-a7575oci.ap-southeast-2.aws.neon.tech/neondb?sslmode=require'
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

use_sqlite = os.environ.get('USE_LOCAL_SQLITE', 'False').lower() in ('true', '1', 't')

if DATABASE_URL and not use_sqlite:
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True if 'sqlite' not in DATABASE_URL.lower() else False
            )
        }
    except Exception:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'hrd_forum.db',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'hrd_forum.db',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudflare R2 (S3-compatible) for uploaded media. Falls back to local MEDIA_ROOT when unset.
# Database FileField values stay as relative keys (e.g. team/KO.jpg); only storage backend changes.
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID', '').strip()
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', '').strip()
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '').strip()
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', 'hrd-forum-media').strip()
R2_PUBLIC_BASE_URL = os.environ.get('R2_PUBLIC_BASE_URL', '').strip().rstrip('/')
USE_R2_STORAGE = bool(R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY)

_STATICFILES_BACKEND = 'whitenoise.storage.CompressedStaticFilesStorage'

if USE_R2_STORAGE:
    AWS_ACCESS_KEY_ID = R2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = R2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
    AWS_S3_REGION_NAME = 'auto'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'path'
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = not bool(R2_PUBLIC_BASE_URL)
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'public, max-age=86400',
    }
    if R2_PUBLIC_BASE_URL:
        AWS_S3_CUSTOM_DOMAIN = R2_PUBLIC_BASE_URL.replace('https://', '').replace('http://', '')
        MEDIA_URL = f'{R2_PUBLIC_BASE_URL}/'
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': _STATICFILES_BACKEND,
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': _STATICFILES_BACKEND,
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
else:
    EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
ADMIN_NOTIFICATION_EMAIL = os.environ.get('ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

# Security & Cookie Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# HSTS & Secure Cookie Enforcements
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 Year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Default Authentication Redirects
LOGIN_URL = '/portal/login/'
LOGIN_REDIRECT_URL = '/portal/'
LOGOUT_REDIRECT_URL = '/portal/login/'
import os
from pathlib import Path
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-hrd-forum-nepal-secret-key-2026')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '*').split(',') if h.strip()]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
        'DIRS': [BASE_DIR, BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'hrd_project.wsgi.application'

# Database Configuration (Serverless compatible)
if os.environ.get('VERCEL') or not os.access(BASE_DIR, os.W_OK):
    db_path = '/tmp/hrd_forum.db'
else:
    db_path = BASE_DIR / 'hrd_forum.db'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_path,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@hrdforum.org')
ADMIN_NOTIFICATION_EMAIL = os.environ.get('ADMIN_NOTIFICATION_EMAIL', 'alerts@hrdforum.org')

# Modern Jazzmin Dashboard Configuration (Flatly theme)
JAZZMIN_SETTINGS = {
    "site_title": "HRD Forum Nepal",
    "site_header": "HRD Forum Nepal",
    "site_brand": "HRD Forum Nepal",
    "welcome_sign": "Welcome to HRD Forum Portal",
    "copyright": "HRD Forum Nepal",
    "search_model": ["main_app.Incident"],
    "custom_css": "css/custom_admin.css",
    "related_modal_active": True,
    
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Emergency Incidents", "url": "admin:main_app_incident_changelist"},
        {"name": "Membership Requests", "url": "admin:main_app_membership_changelist"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Customized sidebar icons for incidents, memberships, news, provinces, etc.
    "icons": {
        "auth": "fas fa-user-shield",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users-cog",
        
        "main_app.Incident": "fas fa-exclamation-triangle",
        "main_app.Membership": "fas fa-id-card",
        "main_app.News": "fas fa-newspaper",
        "main_app.Province": "fas fa-map-marked-alt",
        
        "main_app.Resource": "fas fa-file-alt",
        "main_app.GatedDownloadLead": "fas fa-download",
        "main_app.Gallery": "fas fa-images",
        "main_app.Blog": "fas fa-edit",
        "main_app.Video": "fas fa-video",
        "main_app.TeamMember": "fas fa-users",
        "main_app.Collaboration": "fas fa-handshake",
        "main_app.NewsFlash": "fas fa-bolt",
        "main_app.PopupConfig": "fas fa-bullhorn",
        "main_app.Stats": "fas fa-chart-bar",
        "main_app.UniqueVisitor": "fas fa-eye",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",

    "order_with_respect_to": [
        "main_app.Incident",
        "main_app.Membership",
        "main_app.News",
        "main_app.Province",
        "main_app.Resource",
        "main_app.GatedDownloadLead",
        "main_app.Gallery",
        "main_app.Blog",
        "main_app.Video",
        "main_app.TeamMember",
        "main_app.Collaboration",
        "main_app.NewsFlash",
        "main_app.PopupConfig",
        "main_app.Stats",
        "main_app.UniqueVisitor",
        "auth",
    ],

    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": None,
    "navbar": "navbar-navy navbar-dark",
    "sidebar": "sidebar-dark-navy",
    "brand_colour": "navbar-navy",
    "accent": "accent-info",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "actions_sticky_top": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
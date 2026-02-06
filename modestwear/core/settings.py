from pathlib import Path
import os, sys
from datetime import timedelta
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl
import dj_database_url
from whitenoise.middleware import WhiteNoise

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
from decouple import config


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default='*', cast=lambda v: [s.strip() for s in v.split(',')])
CSRF_ALLOWED_ORIGINS = [
	"https://*.onrender.com"],

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
	"rest_framework",
	"drf_yasg",
	"rest_framework_simplejwt",
	"rest_framework_simplejwt.token_blacklist",
	"corsheaders",
	"djoser",
	"django_celery_beat",
	"apps.catalog.apps.CatalogConfig",
	"apps.orders.apps.OrdersConfig",
	"apps.users.apps.UsersConfig",
	"apps.outfits.apps.OutfitsConfig",	
]

CORS_ALLOWED_ORIGINS = [
	"https://localhost:8080",
]
# settings.py
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": [
		'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
	"ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
	"REFRESH_TOKEN_LIFETIME": timedelta(days=14),
	"ROTATE_REFRESH_TOKENS": True,
	"BLACKLIST_AFTER_ROTATION": True,
	"ALGORITHM": "HS256",
	"SIGNING_KEY": SECRET_KEY,
	"AUTH_HEADER_TYPES": ("Bearer",),
	"USER_ID_FIELD": "id",
	"USER_ID_CLAIM": "user_id",
	"AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
	"TOKEN_TYPE_CLAIM": "token_type",
	"BLACKLIST_TIMEOUT": 86400,
}

JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_NAME = "refresh_token"

SESSION_COOKIE_DOMAIN = '.yourdomain.com'

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SESSION_COOKIE_DOMAIN = None

# Redis Cache Configuration
CACHES = {
	"default": {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient",
			"SOCKET_CONNECT_TIMEOUT": 5,
			"SOCKET_TIMEOUT": 5,
			"IGNORE_EXCEPTIONS": True,
        }
    }
}

# Celery Configuration
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Celery Beat Schedule (Periodic Tasks)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tokens': {
        'task': 'apps.users.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'check-low-stock': {
        'task': 'apps.orders.tasks.check_low_stock_alerts',
        'schedule': crontab(minute=0),  # Every hour
    },
}
if CELERY_BROKER_URL.startswith("rediss://"):
	CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": "ssl.CERT_REQUIRED"}
	CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": "ssl.CERT_REQUIRED"}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
	"whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
	"corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database - PostgreSQL with pgvector (Neon)
if os.getenv("DATABASE_URL"):
# Add these at the top of your settings.py


# Replace the DATABASES section of your settings.py with this
    tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': tmpPostgres.path.replace('/', ''),
            'USER': tmpPostgres.username,
            'PASSWORD': tmpPostgres.password,
            'HOST': tmpPostgres.hostname,
            'PORT': 5432,
            'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.store.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"

EMAIL_VERIFICATION_TIMEOUT = 3600 *24*3

MOBILE_VERIFICATION_REDIRECT = True #Enable mobile app redirection for verfication

REQUIRE_EMAIL_VERIFICATION = True #Whether to require email verification to use the app
APP_NAME = 'Modestwear'

# Email settings
# Using Gmail SMTP

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = 'modestwear <noreply@yourapp.com>'
CONTACT_EMAIL = 'support@modestwear'
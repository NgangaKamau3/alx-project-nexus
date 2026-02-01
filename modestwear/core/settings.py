from pathlib import Path
import os, sys
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-of6k8gill4-!7ocifyieten3f7a0j=w4b5u8n(7f&1=+h*^5_s"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
	"rest_framework.authtoken",
	"corsheaders",
	"djoser",
	"apps.catalog.apps.CatalogConfig",
	"apps.orders.apps.OrdersConfig",
	"users",
	"outfits",	
]

CORS_ALLOWED_ORIGINS = [
	"https://localhost:8080",
]
# settings.py
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": {
		'rest_framework_simplejwt.authentication.JWTAuthenication',
    },
	"DEFAULT_PERMISSION_CLASSES": {
		"rest_framework_permissions.IsAuthenticated",
    },
}

SIMPLE_JWT = {
	"ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
	"REFRESH_TOKEN_LIFETIME": timedelta(days=14),
	"ROTATE_REFRESH_TOKEN": True,
	"BLACLIST_AFTER_ROTATION": True,
	"ALGORITHM": "HS256",
	"SIGNING_KEY": SECRET_KEY,
	"AUTH_HEADER_TYPES": ("Bearer"),
	"USER_ID_FIELD": "id",
	"USER_ID_CLAIM": "user_id",
	"AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AcessToken",),
	"TOKEN_TYPE_CLAIM": "token_type", 
}

JWT_COOKIE_SECURE = False # Set to True in prod!
JWT_COOKIE_NAME = "refresh_token"

CACHE = {
	"default": {
		"BACKEND": "django.core.cache.backends.redis.RedisCache",
		"LOCATION": "redis://localhost:6379/0",
		"TIMEOUT": 3600,
		"OPTIONS": {
			"CLIENT_CLASS": "django.redis.client.DefaultClient",
			"SOCKET_CONNECT_TIMEOUT": 5,
			"SOCKET_TIMEOUT": 5,
			"IGNORE_EXCEPTIONS": True,
        }
    }
}

CACHES = {
	"default": {
		"BACKEND": "django.core.cache.backends.locmem.LocMemCache",
		"LOCATION": "unique-snowflake",		
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [],
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


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"

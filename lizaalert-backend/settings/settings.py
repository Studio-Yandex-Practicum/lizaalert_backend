import os
from datetime import timedelta
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY", "django-insecure-71lo1($*i%(=yl@51%3$1hd@!g-f=tojdt+c5agn$-oin+yu5w")

DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ['0.0.0.0', ])
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://0.0.0.0:8000"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3-rd party apps
    "rest_framework",
    "easy_thumbnails",
    "phonenumber_field",
    "drf_yasg",
    # 3-rd party authentication apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # lizaalert apps
    "users",
    "courses",
    "quizzes",
    "authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "settings.wsgi.application"

DB_SCHEME = env.str("DB_NAME", "")

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": env.str("DB_NAME", "my_database"),
            "USER": env.str("DB_USER", "default_usr"),
            "PASSWORD": env.str("DB_PASSWORD", "password"),
            "HOST": env.str("DB_HOST", "localhost"),
            "PORT": env.int("DB_PORT", 5432),
            "OPTIONS": {"options": f"-c search_path=public{',' + DB_SCHEME}"},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation" ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ]
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}
SITE_ID = 1
REST_USE_JWT = True
REST_AUTH_TOKEN_MODEL = None
REST_AUTH_SERIALIZERS = {"JWT_SERIALIZER": "authentication.serializers.CustomJWTSerializer"}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_ADAPTER = "authentication.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "authentication.adapters.SocialAccountAdapter"
SOCIALACCOUNT_PROVIDERS = {
    "yandex": {
        "APP": {
            "client_id": env.str("YANDEX_CLIENT_ID", "a0693bfc6f9a4a8593e9cfc3a6b34c66"),
            "secret": env.str("YANDEX_SECRET", "d449d272d3f14c308610d3f65e5d3d1f"),
        },
        "VERIFIED_EMAIL": True,
    }
}

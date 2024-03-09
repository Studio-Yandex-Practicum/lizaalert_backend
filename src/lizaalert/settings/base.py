import os
from datetime import timedelta
from pathlib import Path

import sentry_sdk
from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str("SECRET_KEY", "django-insecure-71lo1($*i%(=yl@51%3$1hd@!g-f=tojdt+c5agn$-oin+yu5w")

DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    [
        "la-testing.ru",
        "api.la-testing.ru",
        "admin.la-testing.ru",
        "docs.la-testing.ru",
        "swagger.la-testing.ru",
        "0.0.0.0",
        "127.0.0.1",
        "localhost",
    ],
)

CORS_ALLOWED_ORIGINS = [
    "https://swagger.la-testing.ru",
    "https://docs.la-testing.ru",
    "http://localhost:3000",
    "http://localhost:80",
]

CSRF_TRUSTED_ORIGINS = [
    "https://swagger.la-testing.ru",
    "https://docs.la-testing.ru",
    "http://localhost:3000",
    "http://localhost:80",
]

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
    "corsheaders",
    "django_filters",
    "minio_storage",
    # 3-rd party authentication apps
    "djoser",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # lizaalert apps
    "lizaalert.users",
    "lizaalert.courses",
    "lizaalert.quizzes",
    "lizaalert.authentication",
    "lizaalert.homeworks",
    "lizaalert.webinars",
]

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

ROOT_URLCONF = "lizaalert.settings.urls"

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

WSGI_APPLICATION = "lizaalert.settings.wsgi.application"

DB_SCHEME = env.str("DB_NAME", "")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DB_NAME", "my_database"),
        "USER": env.str("DB_USER", "default_usr"),
        "PASSWORD": env.str("DB_PASSWORD", "password"),
        "HOST": env.str("DB_HOST", "localhost"),
        "PORT": env.int("DB_PORT", 5432),
        "OPTIONS": {
            "sslmode": env.str("DB_SSLMODE", "disable"),
            # "options": f"-c search_path=public{',' + DB_SCHEME}",
        },
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

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_CLASSES = [
    "djoser.views.TokenCreateView",
]

# https://djoser.readthedocs.io/en/latest/settings.html
DJOSER = {
    "LOGIN_FIELD": "email",
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "SET_PASSWORD_RETYPE": True,
    "ACTIVATION_URL": False,
}

YANDEX_INFO_URL = "https://login.yandex.ru/info?format=json"

# https://djoser.readthedocs.io/en/latest/authentication_backends.html#json-web-token-authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# https://drf-yasg.readthedocs.io/en/stable/security.html
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Basic": {"type": "basic"},
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    "LOGIN_URL": "/admin/login/",
    "LOGOUT_URL": "/admin/logout/",
}

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

SITE_ID = 1
REST_USE_JWT = True
REST_AUTH_TOKEN_MODEL = None
ACCOUNT_EMAIL_REQUIRED = True

USE_X_FORWARDED_HOST = True

API_URL = env.str("API_URL", None)


# Sentry logging and monitoring
if sentry_key := env.str("SENTRY_KEY", default=None):
    sentry_sdk.init(
        dsn=env.str("SENTRY_KEY"),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

STATIC_URL = "/static/"
STATIC_ROOT = "./static_files/"

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = "s3:9000"
MINIO_STORAGE_ACCESS_KEY = "admin"
MINIO_STORAGE_SECRET_KEY = "password"
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}
MINIO_STORAGE_MEDIA_BUCKET_NAME = "media"
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = "Recycle Bin"
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = "%c/"
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = "static"
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
DJANGO_HOST = os.environ.get("DJANGO_HOST", "localhost")
MINIO_STORAGE_MEDIA_URL = f"http://{DJANGO_HOST}:9000/media/"

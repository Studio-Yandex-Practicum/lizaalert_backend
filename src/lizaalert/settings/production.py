from lizaalert.settings.base import *  # noqa

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOWED_ORIGINS = [
    "https://swagger.la-testing.ru",
    "https://docs.la-testing.ru",
    "http://localhost:3000",
    "http://localhost:80",
]

CSRF_TRUSTED_ORIGINS = [
    "api.la-testing.ru",
    "admin.la-testing.ru",
    "swagger.la-testing.ru",
    "docs.la-testing.ru",
    "localhost:3000",
    "localhost:80",
]

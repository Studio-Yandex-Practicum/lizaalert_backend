from django.conf import settings


def custom_settings(request):
    return {
        "YANDEX_OAUTH2_KEY": settings.SOCIAL_AUTH_YANDEX_OAUTH2_KEY,
        "YANDEX_OAUTH2_SECRET": settings.SOCIAL_AUTH_YANDEX_OAUTH2_SECRET,
        "YANDEX_REDIRECT_URI": settings.YANDEX_REDIRECT_URI,
    }

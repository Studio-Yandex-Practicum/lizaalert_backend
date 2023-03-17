from allauth.socialaccount.providers.yandex.provider import YandexProvider


class YandexCustomProvider(YandexProvider):
    pass


provider_classes = (YandexCustomProvider,)

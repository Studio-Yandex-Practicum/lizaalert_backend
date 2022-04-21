import requests

from allauth.account.utils import user_email, user_field, user_username
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.utils import valid_email_or_none
from django.conf import settings


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Изменен способ предзаполнения поля username нового пользователя.
        Теперь туда попадает первая часть из поля email (до знака @).
        """
        user = sociallogin.user
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        user_email(user, valid_email_or_none(email) or "")
        username = email.split('@')[0] if email else None
        user_username(user, username or "")
        user_field(user, "first_name", first_name)
        user_field(user, "last_name", last_name)
        return user


class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Если при авторегистрации нового пользователя, username, полученный
        на предварительной стадии из email, при проверки окажется уже занят,
        тогда код выполняющийся до этой функции, сбросит username в пустую строку.

        Но мы точно хотим, чтобы функция generate_unique_username(), которая генерирует
        рандомный суффикс к слову, отталкилавалась все же от email, а не создавала
        однобуквенные имена из пустой строки.

        Ожидаемые рандомные имена будут иметь суффикс вида username[ddddlll],
        где d-случайная цифра, l-сулчайная буква.

        Пример: liza@yandex.ru => liza, liza5, liza4, liza16, liza9894asd
        """
        from allauth.account.utils import user_email, user_username

        assumed_username = user_email(user).split('@')[0]
        username = user_username(user) or self.generate_unique_username([assumed_username])
        user_username(user, username)


class YandexCustomAdapter(YandexAuth2Adapter):
    if settings.LANGUAGE_CODE.lower() == "ru-ru":
        authorize_url = "https://oauth.yandex.ru/authorize"

    def complete_login(self, request, app, token, **kwargs):
        """
        Изменен способ передачи токена при GET-запросе на более безопасный - через
        header (согласно рекомендациям Yandex.API).
        """
        resp = requests.get(
            self.profile_url,
            headers={"Authorization": "OAuth " + token.token},
            params={"format": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)

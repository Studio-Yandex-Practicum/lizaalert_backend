import uuid

import requests
from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.yandex.views import YandexAuth2Adapter
from allauth.utils import email_address_exists, valid_email_or_none
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        # Функция незначительно переписана, чтобы исключить 500 ошибку.
        auto_signup = app_settings.AUTO_SIGNUP
        if auto_signup:
            email = user_email(sociallogin.user)
            if email:
                if account_settings.UNIQUE_EMAIL and email_address_exists(email):
                    # Мы в состоянии регистрации нового уникального SocialAccount().
                    # Нужно создать под это нового пользователя и дать ему почту из
                    # SocialAccount(). Но оказывается, что такая почта уже существует в
                    # таблицах EmailAddress или User, и при этом не связана ни с одним
                    # SocialAccount(). Скорее всего пользователь был создан через
                    # админку с указанием этой почты. Выбрасываем ошибку, поскольку
                    # автоматическое разрешение таких конфликтов не реализовано и
                    # произойдет редирект на несуществующий эндпоинт.
                    # TODO Реализовать связывание нового соцаккаунта и существующего
                    # TODO пользователя, считая, что мы доверяем админке, а другие
                    # TODO пути в это состояние перекрыты.
                    raise AuthenticationFailed(f"Пользователь с почтой {email} уже существует.")
            elif app_settings.EMAIL_REQUIRED:
                auto_signup = False
        return auto_signup  # noqa: R504

    def populate_user(self, request, sociallogin, data):
        # Изменен способ предзаполнения поля username нового пользователя
        # на случайно сгенерированный UUID.
        username = str(uuid.uuid4())
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        user = sociallogin.user
        user_username(user, username or "")
        user_email(user, valid_email_or_none(email) or "")
        user_field(user, "first_name", first_name)
        user_field(user, "last_name", last_name)
        return user


class AccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        raise AuthenticationFailed("inactive user")


class YandexCustomAdapter(YandexAuth2Adapter):
    if settings.LANGUAGE_CODE.lower() == "ru-ru":
        authorize_url = "https://oauth.yandex.ru/authorize"

    def complete_login(self, request, app, token, **kwargs):
        # Изменен способ передачи токена при GET-запросе на более безопасный - через
        # header (согласно рекомендациям Yandex.API).
        resp = requests.get(
            self.profile_url,
            headers={"Authorization": "OAuth " + token.token},
            params={"format": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)

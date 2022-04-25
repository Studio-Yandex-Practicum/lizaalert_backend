from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse


class CustomJWTSerializer(serializers.Serializer):
    """
    Сериалайзер по умолчанию заменен на этот, чтобы исключить
    лишнюю информацию в ответе и возвращать только access_token и
    refresh_token.
    """

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class YandexLoginSerializer(SocialLoginSerializer):
    def set_callback_url(self, view, adapter_class):
        self.callback_url = getattr(view, "callback_url", None)
        if not self.callback_url:
            try:
                self.callback_url = reverse(
                    viewname=adapter_class.provider_id + "_callback",
                    request=self._get_request(),
                )
            except NoReverseMatch:
                raise serializers.ValidationError(
                    _("Define callback_url in view"),
                )

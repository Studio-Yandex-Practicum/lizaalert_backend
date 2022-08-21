from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.http import urlencode
from django.views import View
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .adapters import YandexCustomAdapter
from .provider import YandexCustomProvider
from .serializers import YandexLoginSerializer


class YandexLoginView(View):
    """Перенаправляет пользователя в авторизационный сервис для получения кода подтверждения."""

    provider = YandexCustomProvider
    adapter_class = YandexCustomAdapter

    def get_redirect_url(self):
        url = self.request.build_absolute_uri(reverse(self.provider.id + "_callback"))
        return url

    def get_client_id(self, request):
        app = self.provider(request).get_app(request)
        client_id = app.client_id
        return client_id

    def get(self, request):
        auth_url = self.adapter_class.authorize_url
        params = {
            "response_type": "code",
            "client_id": self.get_client_id(request),
            "redirect_uri": self.get_redirect_url(),
        }
        auth_url_with_params = "%s?%s" % (auth_url, urlencode(params))
        return HttpResponseRedirect(auth_url_with_params)


class YandexLoginCallbackView(SocialLoginView):
    """Создает access и refresh JWT-токены на основе ответа от Яндекса.

    Принимает код подтверждения от пользователя, затем меняет его
    на access_token в авторизационном сервисе. Дальше с помощью
    этого access_token`а получает данные пользователя. На основе полученных
    данных генерирует access и refresh JWT-токены пользователю, если тот есть в БД.
    Иначе сначала создает нового пользователя.
    """

    adapter_class = YandexCustomAdapter
    client_class = OAuth2Client
    serializer_class = YandexLoginSerializer
    http_method_names = ("get",)

    def get(self, request):
        if "code" not in request.GET:
            error = request.GET.get("error")
            raise AuthenticationFailed(error)
        code = request.GET["code"]
        self.serializer = self.get_serializer(data={"code": code})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


class LogoutView(APIView):
    """Удаляет session куки у пользователя."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


oauth2_login = YandexLoginView.as_view()
oauth2_callback = YandexLoginCallbackView.as_view()

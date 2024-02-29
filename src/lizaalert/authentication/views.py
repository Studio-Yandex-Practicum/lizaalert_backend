"""Views.

Note:
- generate refresh token  from rest_framework_simplejwt.tokens import RefreshToken
"""
import logging
import smtplib
import socket
from dataclasses import dataclass

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import ResetPasswordSerializer, UserIdSerialiazer, UserSerializer
from .utils import get_new_password

User = get_user_model()

logger = logging.getLogger(__name__)


@dataclass
class YandexUserData:
    uid: int
    login: str


class LoginView(BaseLoginView, TemplateView):
    template_name = "authentication/login.html"
    extra_context = {
        "YANDEX_OAUTH2_KEY": settings.SOCIAL_AUTH_YANDEX_OAUTH2_KEY,
        "YANDEX_REDIRECT_URI": settings.YANDEX_REDIRECT_URI,
    }

    def get(self, request, *args, **kwargs):
        """Получение Oauth-токена от Яндекса."""
        access_token = self.request.GET.get("access_token")
        # access_token = "y0_AgAAAAB0IyrbAAtGKQAAAAD8X8btAADaYatu35tAWZ9vVM-iY07jlN-F4w"
        if access_token:
            if user_detail := self.get_passport_info(access_token):
                auth_login(self.request, self.get_user(user_detail))
                return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_passport_info(self, access_token):
        """Получаем информацию о пользователе от я.паспорта."""
        url = "https://login.yandex.ru/info"
        headers = {"Authorization": f"OAuth {access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return YandexUserData(user_data["id"], user_data["login"])
        return None

    def get_user(self, user_detail):
        """
        Получение пользователя.

        Если пользователь отсутствует в базе,
        то в базе создается новый пользователь на основании информации,
        полученной от я.паспорта.
        """
        user = User.objects.get_or_create(id=user_detail.uid, username=user_detail.login)
        return user


class CustomCreateUser(APIView):
    """New user registration."""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="New user registration",
        responses={
            201: UserIdSerialiazer,
            400: "Bad request",
        },
    )
    def post(self, request, *args, **kwargs):
        # serializer_class = self.get_serializer(request.data)
        data = JSONParser().parse(request)

        serializer = UserSerializer(data=data)
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = serializer.save()

            response_data = UserIdSerialiazer(data={"id": user.id})
            if response_data.is_valid():
                return JsonResponse(response_data.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_418_IM_A_TEAPOT)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomResetUserPassword(APIView):
    """Create new user backend."""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        operation_description="Reset password, and mail new ",
        responses={
            200: "Change password, send mail",
            400: "Bad request",
            422: "Can't find email",
            424: "Mail server crushed",
        },
    )
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            new_password = get_new_password()
            user.set_password(new_password)
            user.save()
            try:
                send_mail(
                    "ЛизаАлерт subject",
                    f"Ваш новый пароль: {new_password} Для безопасности поменяйте его в личном кабинете",
                    None,
                    [email],
                    fail_silently=False,
                )
            except (smtplib.SMTPException, socket.error) as ex:
                logger.error(f"Can't send mail {ex}")
                return Response(status=status.HTTP_424_FAILED_DEPENDENCY)

            return Response(status=status.HTTP_200_OK)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HiddenTestAuth(APIView):
    """Специальный endpoint не отображается в swagger используется для теста настроек системы авторизации."""

    swagger_schema = None
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user and request.user.username == "test_user":
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

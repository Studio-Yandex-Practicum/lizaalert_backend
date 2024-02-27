"""Views.

Note:
- generate refresh token  from rest_framework_simplejwt.tokens import RefreshToken
"""
import logging
import smtplib
import socket
from collections import namedtuple

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from lizaalert.authentication.serializers import (
    OauthTokenSerializer,
    ResetPasswordSerializer,
    UserIdSerialiazer,
    UserSerializer,
    YandexResponseStatusSerializer,
)
from lizaalert.authentication.utils import get_new_password

User = get_user_model()

logger = logging.getLogger(__name__)


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


class TokenExchange(APIView):
    """
    Замена OAuth-токена Яндекс ID на JWT-токен.

    Методы:
    - POST: Принимает OAuth-токен Яндекс, Возвращает acsess и refresh JWT-токены.

    """

    class YandexStatus:
        def __init__(self, status):
            self.yandex_response_status = status

    class Tokens:
        def __init__(self, refresh, access):
            self.refresh = refresh
            self.access = access

    permission_classes = [AllowAny]
    UserData = namedtuple("UserData", ("id", "login"))
    StatusCode = namedtuple("StatusCode", ("yandex_response_status",))

    @swagger_auto_schema(
        operation_description="Принимает OAuth-токен Яндекс, Возвращает acsess и refresh JWT-токены",
        request_body=OauthTokenSerializer,
        responses={
            201: TokenRefreshSerializer,
            401: YandexResponseStatusSerializer,
        },
    )
    def post(self, request):
        yandex_user_data, status_code = self.get_yandex_user_data(request.data["oauth_token"])
        if not yandex_user_data:
            serializer = YandexResponseStatusSerializer(status_code)
            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
        user, _ = User.objects.get_or_create(id=int(yandex_user_data.id), username=yandex_user_data.login)
        refresh = RefreshToken.for_user(user)
        tokens = self.Tokens(str(refresh), str(refresh.access_token))
        return Response(TokenRefreshSerializer(tokens).data, status=status.HTTP_201_CREATED)

    def get_yandex_user_data(self, oauth_token):
        headers = {"Authorization": f"OAuth {oauth_token}"}
        request = requests.get(settings.YANDEX_INFO_URL, headers=headers)
        if request.status_code == status.HTTP_200_OK:
            request_data = request.json()
            user_data = self.UserData(request_data["id"], request_data["login"])
        else:
            user_data = None
        return user_data, self.YandexStatus(request.status_code)

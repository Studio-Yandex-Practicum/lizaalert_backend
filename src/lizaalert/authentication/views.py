"""Views.

Note:
- generate refresh token  from rest_framework_simplejwt.tokens import RefreshToken
"""
import logging
import requests
import smtplib
import socket

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from lizaalert.settings.base import YANDEX_INFO_URL
from .serializers import ResetPasswordSerializer, UserIdSerialiazer, UserSerializer
from .utils import get_new_password

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

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Принимает OAuth-токен Яндекс, Возвращает acsess и refresh JWT-токены",
        request_body={"oauth_token": "OAuth-токен Яндекс"},
        responses={
            201: {"refresh": "refresh JWT-token", "access": "access JWT-token"},
            401: "Bad request",
        },
    )
    def post(self, request):
        yandex_user_data, status_code = self.get_yandex_user_data(request.data['oauth_token'])
        if not yandex_user_data:
            return Response({"yandex_response_status": status_code}, status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get_or_create(username=yandex_user_data["login"], yandex_id=int(yandex_user_data["id"]))[0]
        refresh = RefreshToken.for_user(user)
        data = {"refresh": str(refresh), "access": str(refresh.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def get_yandex_user_data(oauth_token):
        url = f"{YANDEX_INFO_URL}format=json"
        headers = {"Authorization": f"OAuth {oauth_token}"}
        request = requests.get(url, headers=headers)
        if request.status_code == requests.codes.ok:
            user_data = {"id": request.json()["id"], "login": request.json()["login"]}
        else:
            user_data = None
        return user_data, request.status_code

"""Views.

Note:
- generate refresh token  from rest_framework_simplejwt.tokens import RefreshToken
"""
import logging
import smtplib
import socket

from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.mail import send_mail
from django.http import JsonResponse
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


class LoginView(BaseLoginView):
    template_name = 'authentication/login.html'

    def get_passport_info(self, access_token):
        # curl 'https://login.yandex.ru/info?format=json' -H 'Authorization: OAuth y0_AgAAAAABMdiSAAn0cwAAAADj4WM5iQQPi4GWQXud_lHF_db1oBhW490')
        if status == 200:
            return {"id": "20043922", "login": "ndcomp", "client_id": "48ffa8bf752e49a988525882568e8022", "display_name": "ndcomp", "real_name": "\u0414\u0435\u043d\u0438\u0441 \u041c\u043e\u0441\u043a\u043e\u0432\u0447\u0435\u043d\u043a\u043e", "first_name": "\u0414\u0435\u043d\u0438\u0441", "last_name": "\u041c\u043e\u0441\u043a\u043e\u0432\u0447\u0435\u043d\u043a\u043e", "sex": "male", "default_email": "ndcomp@yandex.ru", "emails": ["ndcomp@yandex.ru"], "default_avatar_id": "0/0-0", "is_avatar_empty": True, "psuid": "1.AAn0cw.Ih177p5BWMrgjBYbHBLITg.CRqswaxP9sXOwT9vbEn9CA"}
        return None
    
    def get_user(self, user_detail):
        # get or create
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

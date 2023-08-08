import random
import string

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import logout, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import reverse
from django.utils.http import urlencode
from django.views import View
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lizaalert.authentication.adapters import YandexCustomAdapter
from lizaalert.authentication.provider import YandexCustomProvider
from .utils import send_new_password


User = get_user_model()

@api_view(["POST"])
def reset_password(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "User not found"})
    new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
    user.set_password(new_password)
    user.save()
    send_new_password(
        email,
        f"Ваш новый пароль: {new_password}. Для безопасности поменяйте его в личном кабинете",
    )
    return JsonResponse({"message": "Password reset successfully"})

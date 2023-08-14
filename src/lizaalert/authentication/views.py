import random
import string

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .utils import send_new_password

User = get_user_model()


@api_view(["POST"])
def reset_password(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "User not found"})
    new_password = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
    user.set_password(new_password)
    user.save()
    send_new_password(
        email,
        f"Ваш новый пароль: {new_password}. \
        Для безопасности поменяйте его в личном кабинете",
    )

    return JsonResponse({"message": "Password reset successfully"})


@api_view(["POST"])
def custom_register(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response_data = {
        "user": {
            "username": user.username,
            "email": user.email,
            "id": user.id,
        },
        "access_token": access_token,
        "refresh_token": str(refresh),
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

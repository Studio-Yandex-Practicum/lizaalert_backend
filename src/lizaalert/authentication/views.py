import random
import string

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.decorators import api_view

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

from django.urls import path

from lizaalert.authentication.provider import YandexCustomProvider
from . import views


urlpatterns = [
    path("auth/users/reset_password/", views.reset_password, name="reset_password"),
]

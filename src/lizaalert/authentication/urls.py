from django.urls import path

from . import views

urlpatterns = [
    path("auth/users/reset_password/", views.reset_password, name="reset_password"),
    path("auth/users/", views.custom_register, name="custom_register"),
]

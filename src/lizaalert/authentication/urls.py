from django.urls import path

from . import views

urlpatterns = [
    path("auth/users/reset_password/", views.CustomResetUserPassword.as_view(), name="reset_password"),
    # path("auth/users/reset_password/", views.reset_password, name="reset_password"),
    # path("auth/users/", views.custom_register, name="custom_register"),
    path("auth/users/", views.CustomCreateUser.as_view(), name="custom_register"),
]

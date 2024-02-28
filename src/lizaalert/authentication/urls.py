from django.urls import path

from . import views

urlpatterns = [
    path("auth/users/reset_password/", views.CustomResetUserPassword.as_view(), name="reset_password"),
    path("auth/users/", views.CustomCreateUser.as_view(), name="custom_register"),
    path("auth/users/test/", views.HiddenTestAuth.as_view(), name="test_auth"),
    path("auth/token/create/", views.TokenExchange.as_view(), name="token_exchange"),
]

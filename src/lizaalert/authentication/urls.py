from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from lizaalert.authentication.provider import YandexCustomProvider
from lizaalert.authentication.views import LogoutView

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
]
urlpatterns += default_urlpatterns(YandexCustomProvider)

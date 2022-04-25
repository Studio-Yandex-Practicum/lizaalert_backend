from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .provider import YandexCustomProvider

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
urlpatterns += default_urlpatterns(YandexCustomProvider)

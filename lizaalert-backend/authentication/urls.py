from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import YandexCustomProvider

urlpatterns = []
urlpatterns += default_urlpatterns(YandexCustomProvider)

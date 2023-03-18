from allauth.socialaccount.models import SocialApp, SocialToken
from django.contrib import admin

# Убираем из админки неиспользуемые модели, добавляемые django allauth по умолчанию.
# Данное приложение ("authentication") должно быть ниже,
# чем "allauth.socialaccount" в INSTALLED_APPS.
models = (SocialToken, SocialApp)
for model in models:
    if admin.site.is_registered(model):
        admin.site.unregister(model)

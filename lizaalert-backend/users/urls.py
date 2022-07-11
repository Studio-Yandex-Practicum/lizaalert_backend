from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import LevelViewSet

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")

urlpatterns = [
    path("", include(router.urls)),
]

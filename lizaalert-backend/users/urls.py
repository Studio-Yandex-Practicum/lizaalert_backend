from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LevelViewSet, ListRoles

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")

urlpatterns = [
    path("", include(router.urls)),
    path("roles/", ListRoles.as_view())
]

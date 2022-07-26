from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LevelViewSet, ListRoles, UserRoleViewSet

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")
router.register(r"users/(?P<user_id>\d+)/role", UserRoleViewSet, basename="user_role")

urlpatterns = [
    path("", include(router.urls)),
    path("roles/", ListRoles.as_view())
]

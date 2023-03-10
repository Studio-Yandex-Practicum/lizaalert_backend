from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LevelViewSet, ListRoles, UserRoleViewSet, VolunteerAPIview

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")
router.register(r"users/(?P<user_id>\d+)/roles", UserRoleViewSet, basename="user_roles")

urlpatterns = [
    path("profile/", VolunteerAPIview.as_view(), name="profile"),
    path("roles/", ListRoles.as_view()),
    path("", include(router.urls)),
]

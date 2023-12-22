from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lizaalert.users.views import LevelViewSet, ListRoles, UserRoleViewSet, VolunteerAPIview, VolunteerBadgeList

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")
router.register(r"users/(?P<user_id>\d+)/roles", UserRoleViewSet, basename="user_roles")

urlpatterns = [
    path("profile/", VolunteerAPIview.as_view(), name="profile"),
    path("profile/badges/", VolunteerBadgeList.as_view(), name="badgeslist"),
    path("roles/", ListRoles.as_view()),
    path("", include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lizaalert.users.views import (
    BadgeVolunteerListView,
    LevelViewSet,
    ListRoles,
    UserRoleViewSet,
    VolunteerAPIview,
    VolunteerBadgeListViewSet,
)

router = DefaultRouter()
router.register(r"level", LevelViewSet, basename="level")
router.register(r"users/(?P<user_id>\d+)/roles", UserRoleViewSet, basename="user_roles")
router.register(r"profile/badges", VolunteerBadgeListViewSet, basename="badgeslist")
router.register(
    r"volunteers/(?P<badge_slug>[a-z0-9]+)", BadgeVolunteerListViewSet, basename="volunteerbadgelist")

urlpatterns = [
    path("volunteers/<slug:badge_slug>/", BadgeVolunteerListView.as_view(), name="volunteerbadgelist"),
    path("profile/", VolunteerAPIview.as_view(), name="profile"),
    path("roles/", ListRoles.as_view()),
    path("", include(router.urls)),
]

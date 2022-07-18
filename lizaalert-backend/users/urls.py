from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import LevelViewSet, ListRoles, VolunteerAPIview


urlpatterns = [
    path("profile/", VolunteerAPIview.as_view(), name="profile"),
    path("level/", LevelViewSet.as_view(), basename="level"),
    path("roles/", ListRoles.as_view())
]

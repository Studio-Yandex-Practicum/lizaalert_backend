from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import CourseStatusViewSet

router = DefaultRouter()
router.register(r"course_statuses", CourseStatusViewSet, basename="users")

urlpatterns = [
    path("users/", include(router.urls)),
]

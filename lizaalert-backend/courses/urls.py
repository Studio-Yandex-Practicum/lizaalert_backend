from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseStatusViewSet, CourseViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"courses_statuses", CourseStatusViewSet, basename="courses_statuses")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from lizaalert.courses.views import LessonViewSet, CourseStatusViewSet, CourseViewSet, FilterListViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"courses_statuses", CourseStatusViewSet, basename="courses_statuses"),
router.register("filters", FilterListViewSet, basename="filters-list")
router.register("lessons", LessonViewSet, basename="lessons")

domains_router = routers.NestedSimpleRouter(router, r"courses", lookup="courses")

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(domains_router.urls)),
]

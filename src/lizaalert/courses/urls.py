from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from lizaalert.courses.views import CourseLessonListViewSet, CourseStatusViewSet, CourseViewSet, FilterListViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"courses_statuses", CourseStatusViewSet, basename="courses_statuses"),
router.register("filters", FilterListViewSet, basename="filters-list")

domains_router = routers.NestedSimpleRouter(router, r"courses", lookup="courses")
domains_router.register(r"lessons", CourseLessonListViewSet, basename="course-chapters-list")

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(domains_router.urls)),
]

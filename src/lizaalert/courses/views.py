from django.db.models import CharField, Count, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from lizaalert.courses.filters import CourseFilter
from lizaalert.courses.models import Course, CourseStatus, Lesson
from lizaalert.courses.pagination import CourseSetPagination
from lizaalert.courses.serializers import (
    CourseDetailSerializer,
    CourseLessonListSerializer,
    CourseSerializer,
    CourseStatusSerializer,
    FilterSerializer,
)
from lizaalert.users.models import Level


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        AllowAny,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CourseFilter
    filterset_fields = ("level", "course_format")
    pagination_class = CourseSetPagination

    def get_queryset(self):
        user = self.request.user
        lesson_status = Lesson.LessonStatus.READY
        if user.is_authenticated:
            course = Course.objects.all().annotate(
                course_duration=Sum(
                    "chapters__lessons__duration",
                    filter=Q(chapters__lessons__lesson_status=lesson_status),
                ),
                lessons_count=Count(
                    "chapters__lessons",
                    filter=Q(chapters__lessons__lesson_status=lesson_status),
                ),
                course_status=(
                    Coalesce(
                        Subquery(
                            Course.objects.filter(
                                course_volunteers__volunteer__user=user,
                                id=OuterRef("id"),
                            ).values("course_volunteers__status__slug"),
                            output_field=CharField(),
                        ),
                        Value("inactive"),
                    )
                ),
            )
            return course
        course = Course.objects.all().annotate(
            course_duration=Sum(
                "chapters__lessons__duration",
                filter=Q(chapters__lessons__lesson_status=lesson_status),
            ),
            lessons_count=Count(
                "chapters__lessons",
                filter=Q(chapters__lessons__lesson_status=lesson_status),
            ),
            course_status=Value("inactive"),
            user_status=Value("not_enrolled")
        )
        return course

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [IsAuthenticated]


class CourseLessonListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseLessonListSerializer

    def get_queryset(self):
        out = Lesson.objects.filter(chapter__course__id=self.kwargs["courses_pk"])
        return out


class FilterListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = [Level, CourseStatus]
    serializer_class = FilterSerializer

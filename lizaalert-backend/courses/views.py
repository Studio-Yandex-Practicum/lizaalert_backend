from django.db.models import CharField, Count, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Course, CourseStatus, Lesson
from .pagination import CourseSetPagination
from .serializers import CourseSerializer, CourseStatusSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [
        AllowAny,
    ]
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
        )
        return course


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [IsAuthenticated]

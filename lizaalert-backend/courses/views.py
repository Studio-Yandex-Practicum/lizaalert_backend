from django.db.models import Sum, Count, Q, F
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Course, CourseStatus
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
        course = Course.objects.annotate(course_duration=Sum('chapters__lessons__duration',
                                                             filter=Q(chapters__lessons__lesson_status='Ready')),
                                         lessons_count=Count('chapters__lessons',
                                                             filter=Q(chapters__lessons__lesson_status='Ready')),
                                         course_status=F('course_volunteers__status__slug'))
        return course


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Course, CourseStatus
from .pagination import CourseSetPagination
from .serializers import CourseSerializer, CourseStatusSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [
        AllowAny,
    ]
    pagination_class = CourseSetPagination


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [
        IsAuthenticated
    ]

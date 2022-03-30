from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Course
from .pagination import CourseSetPagination
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CourseSetPagination

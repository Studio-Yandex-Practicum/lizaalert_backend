from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CourseStatus
from .serializers import CourseStatusSerializer


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [
        AllowAny, IsAuthenticated
    ]

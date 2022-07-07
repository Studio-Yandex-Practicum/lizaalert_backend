from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Level
from .serializers import LevelSerializer


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

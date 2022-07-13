from rest_framework import viewsets

from .models import Level
from .serializers import LevelSerializer


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

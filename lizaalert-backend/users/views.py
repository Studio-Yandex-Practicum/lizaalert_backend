from rest_framework import views, viewsets
from rest_framework.response import Response

from .models import Level, UserRole
from .serializers import LevelSerializer


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer


class ListRoles(views.APIView):
    def get(self, request):
        results = [{"name": name, "description": description} for name, description in UserRole.Role.choices]
        return Response({"results": results})

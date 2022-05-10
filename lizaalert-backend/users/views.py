from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Volunteer
from .serializers import VolunteerSerializer


class VolunteerAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        volunteer = get_object_or_404(Volunteer, pk=user_id)
        serializer = VolunteerSerializer(volunteer,
                                         context={'request': request})
        return Response(serializer.data)

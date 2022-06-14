from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Volunteer
from .serializers import VolunteerSerializer


class VolunteerAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        volunteer = get_object_or_404(Volunteer, user=request.user)
        serializer = VolunteerSerializer(volunteer,
                                         context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        volunteer = get_object_or_404(Volunteer, user=request.user)
        serializer = VolunteerSerializer(volunteer,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

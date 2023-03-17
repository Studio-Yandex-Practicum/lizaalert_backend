from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lizaalert.users.models import Level, User, UserRole, Volunteer
from lizaalert.users.serializers import LevelSerializer, UserRoleSerializer, VolunteerSerializer


class VolunteerAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        volunteer = get_object_or_404(Volunteer, user=request.user)
        serializer = VolunteerSerializer(volunteer, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        volunteer = get_object_or_404(Volunteer, user=request.user)
        serializer = VolunteerSerializer(volunteer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer


class ListRoles(views.APIView):
    def get(self, request):
        results = [{"name": name, "description": description} for name, description in UserRole.Role.choices]
        return Response({"results": results})


class UserRoleViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        get_object_or_404(User, id=user_id)
        new_queryset = UserRole.objects.filter(user=user_id)
        return new_queryset

    def perform_create(self, serializer):
        user_id = self.kwargs.get("user_id")
        user_role = serializer.validated_data.get("role")
        current_user = get_object_or_404(User, id=user_id)
        serializer.save(user=current_user)
        if user_role == UserRole.Role.MAIN_ADMIN:
            current_user.is_superuser = True
            current_user.is_staff = True
            current_user.save()

    def perform_destroy(self, instance):
        current_user = instance.user
        super().perform_destroy(instance)
        if not UserRole.objects.filter(user=current_user, role=UserRole.Role.MAIN_ADMIN).exists():
            current_user.is_superuser = False
            current_user.is_staff = False
            current_user.save()

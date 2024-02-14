from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lizaalert.courses.models import Subscription
from lizaalert.users.models import Badge, Level, User, UserRole, Volunteer, VolunteerBadge
from lizaalert.users.serializers import (
    BadgeSerializer,
    Error400Serializer,
    Error404Serializer,
    LevelSerializer,
    UserRoleSerializer,
    VolunteerSerializer,
)


class VolunteerAPIview(APIView):
    """
    Endpoint для работы с профилем пользователя.

    Методы:
    - GET: Отображение профиля пользователя.
    - PATCH: Внесение изменений в профиль пользователя.

    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Отображает профиль пользователя",
        responses={200: VolunteerSerializer(), 204: "", 404: Error404Serializer()},
    )
    def get(self, request):
        """Получить профиль пользователя."""
        volunteer = get_object_or_404(Volunteer, user=request.user)
        queryset = Volunteer.objects.annotate(
            count_pass_course=Subquery(
                Subscription.objects.filter(
                    course__course_volunteers__volunteer=OuterRef("pk"),
                    user=request.user,
                    status=Subscription.Status.COMPLETED,
                )
                .values("course__course_volunteers__volunteer")
                .annotate(count_pass_course=Count("pk"))
                .values("count_pass_course")[:1]
            )
        ).filter(pk=volunteer.pk)
        serializer = VolunteerSerializer(queryset, context={"request": request}, many=True)
        if queryset:
            return Response(serializer.data[0])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Внесение изменений в профиль пользователя",
        request_body=VolunteerSerializer,
        responses={200: VolunteerSerializer(), 400: Error400Serializer(), 404: Error404Serializer()},
    )
    def patch(self, request):
        """Изменить профиль пользователя."""
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


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description="Список ачивок пользователя",
        manual_parameters=[
            openapi.Parameter(
                name="course",
                required=False,
                type="integer",
                in_="query",
                description="Id курса",
            ),
        ],
        responses={200: BadgeSerializer(), 400: Error400Serializer()},
    ),
)
@method_decorator(name="retrieve", decorator=swagger_auto_schema(auto_schema=None))
class VolunteerBadgeListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Отображение списка ачивок пользователя.

    Методы:
    - GET: Возвращает список ачивок пользователя.

    """

    permission_classes = [IsAuthenticated]
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer

    def get_queryset(self):
        volunteer_badge = VolunteerBadge.objects.filter(volunteer__user=self.request.user)
        if course_id := self.request.query_params.get("course", None):
            volunteer_badge = volunteer_badge.filter(course_id=course_id)
        queryset = super().get_queryset().filter(id__in=volunteer_badge.values("badge_id"))
        return queryset


class BadgeVolunteerListView(ListAPIView):
    """
    Отображение списка волонтёров по ачивке (slug-полю поиска).

    Методы:
    - GET: Возвращает список волонтёров.

    Параметры пагинации:
    - limit: количество объектов на странице,
    - offset: отступ первой страницы.

    Пример: /?limit=3&offset=2

    """

    serializer_class = VolunteerSerializer
    pagination_class = LimitOffsetPagination

    @swagger_auto_schema(
        operation_description="""
        Получение QuerySet для волонтеров имеющих определенный бэйдж.

        Возвращает:
            QuerySet: QuerySet для волонтеров отфильтрованных по полю "badge_slug" в модели Badge.
        """,
        responses={
            200: VolunteerSerializer(),
            400: "Bad Request",
        },
    )
    def get_queryset(self):
        badge_slug = self.kwargs["badge_slug"]
        queryset = Volunteer.objects.filter(badges__badge_slug=badge_slug)
        return queryset

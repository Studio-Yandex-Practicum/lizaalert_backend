from django.db.models import Count, Exists, OuterRef, Q, Subquery, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lizaalert.courses.filters import CourseFilter
from lizaalert.courses.models import Course, CourseStatus, Lesson, LessonProgressStatus, Subscription
from lizaalert.courses.pagination import CourseSetPagination
from lizaalert.courses.permissions import IsUserOrReadOnly
from lizaalert.courses.serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseStatusSerializer,
    FilterSerializer,
    LessonSerializer,
)
from lizaalert.users.models import Level


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for course."""

    permission_classes = [
        AllowAny,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CourseFilter
    filterset_fields = ("level", "course_format")
    pagination_class = CourseSetPagination

    def get_queryset(self):
        """
        Queryset getter.

        base_annotations - provide annotations for both authenticated and
        unauthenticated users.
        users_annotations - provide annotations only for auth user.
        """
        user = self.request.user
        lesson_status = Lesson.LessonStatus.PUBLISHED
        base_annotations = {
            "course_duration": Sum(
                "chapters__lessons__duration",
                filter=Q(chapters__lessons__lesson_status=lesson_status),
            ),
            "lessons_count": Count(
                "chapters__lessons",
                filter=Q(chapters__lessons__lesson_status=lesson_status),
            ),
        }

        if user.is_authenticated:
            users_annotations = {
                "user_status": Exists(Subscription.objects.filter(user=user, enabled=1, course_id=OuterRef("id"))),
            }
            return Course.objects.annotate(**base_annotations, **users_annotations)
        return Course.objects.annotate(**base_annotations)

    def get_serializer_class(self):
        if self.action == "enroll" or self.action == "unroll":
            return None
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    @action(detail=True, methods=["post"], permission_classes=(IsAuthenticated,))
    def enroll(self, request, **kwargs):
        """Subscribe user for given course."""
        user = self.request.user
        course = get_object_or_404(Course, **kwargs)
        Subscription.objects.create(user=user, course=course)
        return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=(
            IsAuthenticated,
            IsUserOrReadOnly,
        ),
    )
    def unroll(self, request, **kwargs):
        """Unsubscribe user from given course."""
        user = self.request.user
        course = get_object_or_404(Course, **kwargs)
        subscription = get_object_or_404(Subscription, user=user, course=course)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseStatus.objects.all()
    serializer_class = CourseStatusSerializer
    permission_classes = [IsAuthenticated]


class LessonViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = LessonSerializer

    def get_queryset(self):
        """
        Create custom queryset for lessons.

        user_lesson_progress - returns the progress (int: id) of current user with the current lesson
        next_lesson_id - returns the int id of the next lesson in current chapter
        prev_lesson_id - returns the int id of the previous lesson in current chapter.
        """
        user = self.request.user
        base_annotations = {
            "user_lesson_progress": Subquery(
                LessonProgressStatus.objects.filter(lesson=OuterRef("id"), user=user)
                .order_by("-updated_at")
                .values("userlessonprogress")[:1]
            ),
            "next_lesson_id": Subquery(
                Lesson.objects.filter(chapter=OuterRef("chapter"), order_number__gt=OuterRef("order_number"))
                .order_by("order_number")
                .values("id")[:1]
            ),
            "prev_lesson_id": Subquery(
                Lesson.objects.filter(chapter=OuterRef("chapter"), order_number__lt=OuterRef("order_number"))
                .order_by("-order_number")
                .values("id")[:1]
            ),
        }
        return Lesson.objects.select_related("chapter").annotate(**base_annotations)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=(
            IsAuthenticated,
            IsUserOrReadOnly,
        ),
    )
    def complete(self, request, **kwargs):
        user = self.request.user
        lesson = get_object_or_404(Lesson, **kwargs)
        lesson.finished = user
        return Response(status=status.HTTP_200_OK)


class FilterListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = [Level, CourseStatus]
    serializer_class = FilterSerializer

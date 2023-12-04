from django.db import transaction
from django.db.models import Count, Exists, F, IntegerField, OuterRef, Prefetch, Q, Subquery, Sum, Value
from django.db.models.functions import Cast, Coalesce
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lizaalert.courses.filters import CourseFilter
from lizaalert.courses.models import (
    Chapter,
    ChapterProgressStatus,
    Course,
    CourseProgressStatus,
    Lesson,
    LessonProgressStatus,
    Subscription,
)
from lizaalert.courses.pagination import CourseSetPagination
from lizaalert.courses.permissions import IsUserOrReadOnly
from lizaalert.courses.serializers import CourseDetailSerializer, CourseSerializer, FilterSerializer, LessonSerializer
from lizaalert.courses.utils import BreadcrumbLessonSerializer, ErrorSerializer
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
                filter=Q(chapters__lessons__status=lesson_status),
            ),
            "lessons_count": Count(
                "chapters__lessons",
                filter=Q(chapters__lessons__status=lesson_status),
            ),
        }

        if user.is_authenticated:
            # Аннотируем прогресс пользователя по главе
            chapters_with_progress = Chapter.objects.annotate(
                user_chapter_progress=Coalesce(
                    Cast(
                        Subquery(
                            ChapterProgressStatus.objects.filter(chapter=OuterRef("id"), user=user)
                            .order_by("-updated_at")
                            .values("userchapterprogress")[:1]
                        ),
                        IntegerField(),
                    ),
                    Value(0),
                )
            )
            # Аннотируем прогресс пользователя по уроку
            lessons_with_progress = Lesson.objects.annotate(
                user_lesson_progress=Coalesce(
                    Cast(
                        Subquery(
                            LessonProgressStatus.objects.filter(lesson=OuterRef("id"), user=user)
                            .order_by("-updated_at")
                            .values("userlessonprogress")[:1]
                        ),
                        IntegerField(),
                    ),
                    Value(0),
                )
            )
            # current lesson - текущий урок (первый урок после незаконченных уроков)
            current_lesson = (
                Lesson.objects.filter(
                    chapter__course=OuterRef("id"),
                    status=Lesson.LessonStatus.PUBLISHED,
                )
                .exclude(
                    lesson_progress__userlessonprogress=LessonProgressStatus.ProgressStatus.FINISHED,
                )
                .annotate(ordering=F("chapter__order_number") + F("order_number"))
                .order_by("ordering")
            )

            users_annotations = {
                "user_status": Exists(Subscription.objects.filter(user=user, enabled=1, course_id=OuterRef("id"))),
                "user_course_progress": Coalesce(
                    Cast(
                        Subquery(
                            CourseProgressStatus.objects.filter(course=OuterRef("id"), user=user)
                            .order_by("-updated_at")
                            .values("usercourseprogress")[:1]
                        ),
                        IntegerField(),
                    ),
                    Value(0),
                ),
                "current_lesson": current_lesson.values("id")[:1],
                "current_chapter": current_lesson.values("chapter_id")[:1],
            }
            return (
                Course.objects.filter(status=Course.CourseStatus.PUBLISHED)
                .annotate(**base_annotations, **users_annotations)
                .prefetch_related(
                    Prefetch("chapters", queryset=chapters_with_progress),
                    Prefetch("chapters__lessons", queryset=lessons_with_progress),
                )
            )
        return Course.objects.filter(status=Course.CourseStatus.PUBLISHED).annotate(**base_annotations)

    def get_serializer_class(self):
        if self.action == "enroll" or self.action == "unroll":
            return None
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    @swagger_auto_schema(responses={201: BreadcrumbLessonSerializer, 403: ErrorSerializer})
    @action(detail=True, methods=["post"], permission_classes=(IsAuthenticated,))
    def enroll(self, request, **kwargs):
        """Subscribe user for given course."""
        user = self.request.user
        course = get_object_or_404(Course, **kwargs)
        check_for_subscription = Subscription.objects.filter(user=user, course=course).exists()
        if check_for_subscription:
            serializer = ErrorSerializer({"error": "Subscription already exists."})
            return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)
        Subscription.objects.create(user=user, course=course)
        current_lesson = course.current_lesson(user).first()
        if current_lesson:
            initial_lesson = {"chapter_id": current_lesson.chapter_id, "lesson_id": current_lesson.id}
        else:
            initial_lesson = {"chapter_id": None, "lesson_id": None}
        serializer = BreadcrumbLessonSerializer(initial_lesson)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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


class LessonViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        """
        Create custom queryset for lessons.

        user_lesson_progress - returns the progress (int: id) of current user with the current lesson
        next_lesson_id - returns the int id of the next lesson in current course
        prev_lesson_id - returns the int id of the previous lesson in current course.
        """
        user = self.request.user
        lesson_id = self.kwargs.get("pk")
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson_with_ordering = lesson.ordered.get(id=lesson_id)
        base_annotations = {
            "next_lesson_id": lesson_with_ordering.next_lesson.values("id"),
            "prev_lesson_id": lesson_with_ordering.prev_lesson.values("id"),
            "next_chapter_id": lesson_with_ordering.next_lesson.values("chapter_id"),
            "prev_chapter_id": lesson_with_ordering.prev_lesson.values("chapter_id"),
        }
        if user.is_authenticated:
            user_annotations = {
                "user_lesson_progress": Coalesce(
                    Cast(
                        Subquery(
                            LessonProgressStatus.objects.filter(lesson=OuterRef("id"), user=user)
                            .order_by("-updated_at")
                            .values("userlessonprogress")[:1]
                        ),
                        IntegerField(),
                    ),
                    Value(0),
                )
            }
            return Lesson.objects.select_related("chapter", "chapter__course").annotate(
                **base_annotations, **user_annotations
            )
        return Lesson.objects.select_related("chapter", "chapter__course").annotate(**base_annotations)

    def get_serializer_class(self):
        if self.action == "complete":
            return None
        return LessonSerializer

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            any_progress = LessonProgressStatus.objects.filter(user=user, lesson=lesson).exists()
            if not any_progress:
                lesson.activate(user)
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
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
        lesson.finish(user)
        return Response(status=status.HTTP_201_CREATED)


class FilterListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = [Level]
    serializer_class = FilterSerializer

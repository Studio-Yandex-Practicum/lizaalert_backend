from django.db import transaction
from django.db.models import Count, F, IntegerField, OuterRef, Prefetch, Q, Subquery, Sum, Value
from django.db.models.functions import Cast, Coalesce
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from lizaalert.courses.exceptions import BadRequestException, SubscriptionDoesNotExist
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
from lizaalert.courses.permissions import CurrentLessonOrProhibited, EnrolledAndCourseHasStarted, IsUserOrReadOnly
from lizaalert.courses.serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    CurrentLessonSerializer,
    FilterSerializer,
    LessonSerializer,
    MessageResponseSerializer,
    UserStatusEnrollmentSerializer,
)
from lizaalert.users.models import Level


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint для работы с курсами.

    Предоставляет операции чтения и дополнительные действия.
    Responses:
        200: Ответ с сериализованными данными курса.
        201: Ответ с сериализованными данными, указывающими характеристики подписки.
    """

    permission_classes = [
        AllowAny,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CourseFilter
    filterset_fields = ("level", "course_format")
    pagination_class = CourseSetPagination

    @swagger_auto_schema(
        operation_description="""
        Получение QuerySet для курсов.

        Этот метод извлекает QuerySet для курсов с аннотациями как для
        аутентифицированных, так и для неаутентифицированных пользователей.

        Возвращает:
            QuerySet: QuerySet для курсов.

        base_annotations содержит аннотации для запроса, которые не зависят от пользователя:

        - course_duration - суммарная продолжительность всех уроков в курсе;
        - lessons_count - количество уроков в курсе.

        user_annotations содержит аннотации для запроса, которые зависят от пользователя:

        - user_status - статус пользователя по отношению к курсу (записался на курс, проходит курс и т.д.);
        - user_course_progress - прогресс пользователя в курсе;
        - current_lesson - текущий урок пользователя;
        - current_chapter - текущая глава пользователя.
        """
    )
    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs.get("pk")
        course = None
        if course_id:
            course = get_object_or_404(Course, id=course_id)
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
            if course:
                current_lesson = course.current_lesson(user)

            else:
                current_lesson = (
                    Lesson.objects.filter(chapter__course=course, status=Lesson.LessonStatus.PUBLISHED)
                    .annotate(ordering=F("chapter__order_number") + F("order_number"))
                    .order_by("ordering")
                )
            # Аннотируем прогресс пользователя по главе
            chapters_with_progress = Chapter.objects.annotate(
                user_chapter_progress=Coalesce(
                    Cast(
                        Subquery(
                            ChapterProgressStatus.objects.filter(chapter=OuterRef("id"), subscription__user=user)
                            .order_by("-updated_at")
                            .values("progress")[:1]
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
                            LessonProgressStatus.objects.filter(lesson=OuterRef("id"), subscription__user=user)
                            .order_by("-updated_at")
                            .values("progress")[:1]
                        ),
                        IntegerField(),
                    ),
                    Value(0),
                )
            )

            users_annotations = {
                "user_status": Coalesce(
                    Subquery(Subscription.objects.filter(user=user, course_id=OuterRef("id")).values("status")),
                    Value("not_enrolled"),
                ),
                "user_course_progress": Coalesce(
                    Cast(
                        Subquery(
                            CourseProgressStatus.objects.filter(course=OuterRef("id"), subscription__user=user)
                            .order_by("-updated_at")
                            .values("progress")[:1]
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
        if self.action in (
            "enroll",
            "unroll",
            "complete",
        ):
            return None
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def _get_current_lesson(self, **kwargs):
        """Вспомогательный метод для получения текущего урока и главы пользователя для курса."""
        user = self.request.user
        try:
            course = get_object_or_404(Course, **kwargs)
        except ValueError:
            raise BadRequestException({"detail": "Invalid id."})

        current_lesson = course.current_lesson(user).first()
        return current_lesson, user, course

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: UserStatusEnrollmentSerializer,
        }
    )
    @action(detail=True, methods=["post"], permission_classes=(IsAuthenticated,))
    def enroll(self, request, **kwargs):
        """
        Подписать пользователя на участие в данном курсе.

        Возвращает:

                201: Ответ с сериализованными данными, указывающими результат подписки.

        Исключения:

                403 Forbidden: Если пользователь уже подписан на данный курс.

        Примечание:
            Это действие требует аутентификации пользователя.

        """
        user = self.request.user
        try:
            course = get_object_or_404(Course, **kwargs)
        except ValueError:
            raise BadRequestException({"detail": "Invalid id."})
        subscription = course.subscribe(user)
        current_lesson = course.current_lesson(user).first()
        serializer = UserStatusEnrollmentSerializer(current_lesson, context={"subscription": subscription})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: "Пользователь успешно отписан от курса.",
        }
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=(
            IsAuthenticated,
            IsUserOrReadOnly,
        ),
    )
    def unroll(self, request, **kwargs):
        """
        Отписать пользователя от участия в данном курсе.

        Примечание:
            Это действие требует аутентификации пользователя и соответствующих прав.

        """
        user = self.request.user
        try:
            course = get_object_or_404(Course, **kwargs)
        except ValueError:
            raise BadRequestException({"detail": "Invalid id."})
        subscription = get_object_or_404(Subscription, user=user, course=course)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: CurrentLessonSerializer,
        }
    )
    @action(detail=True, methods=["get"], permission_classes=(IsAuthenticated,))
    def current_lesson(self, request, **kwargs):
        """
        Получить текущий урок пользователя для курса.

        Возвращает:
                    200: Ответ с сериализованными данными текущего урока пользователя.
                    403: Ответ с сериализованными данными, указывающими на ошибку доступа.
        """
        current_lesson, _, _ = self._get_current_lesson(**kwargs)

        serializer = CurrentLessonSerializer(current_lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: "Курс успешно завершен.",
        }
    )
    @action(detail=True, methods=["post"], permission_classes=(IsAuthenticated, EnrolledAndCourseHasStarted))
    def complete(self, request, **kwargs):
        """
        Завершить курс для пользователя.

        Данное событие вызывает сигнал завершения курса.
        """
        user = self.request.user
        try:
            course = get_object_or_404(Course, **kwargs)
            subscription = get_object_or_404(Subscription, course=course, user=user)
        except ValueError:
            raise BadRequestException({"detail": "Invalid id."})
        course.finish(subscription)
        # Отправить сигнал для получения ачивок
        course.get_achievements(course, user)
        serializer = MessageResponseSerializer(data="Курс успешно завершен")
        return Response(serializer.initial_data, status=status.HTTP_200_OK)


class LessonViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Класс представления для работы с уроками.

    Предоставляет операции чтения и дополнительные действия.

    Атрибуты:
        - permission_classes: Список классов разрешений, разрешающий доступ всем пользователям.

    Методы:
        - get_queryset: Формирует пользовательский запрос для уроков, включая информацию о прогрессе пользователя.

        - get_serializer_class: Возвращает класс сериализатора в зависимости от текущего действия.

        - retrieve: Получает детали урока, активируя его для пользователя при необходимости.

        - complete: Завершает урок для пользователя.

    Примечание:
        Для выполнения дополнительных действий, таких как завершение урока, требуется аутентификация пользователя.

    Responses:
        200: Ответ с сериализованными данными урока.
        201: Ответ с сериализованными данными, указывающими на успешное завершение урока.
        403: Ответ с сериализованными данными, указывающими на ошибку доступа.
    """

    permission_classes = [
        AllowAny,
        CurrentLessonOrProhibited,
        EnrolledAndCourseHasStarted,
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
        if user.is_authenticated:
            try:
                subscription = Subscription.objects.get(course=lesson.chapter.course, user=user)
            except Subscription.DoesNotExist:
                raise SubscriptionDoesNotExist()
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
                            LessonProgressStatus.objects.filter(lesson=OuterRef("id"), subscription=subscription)
                            .order_by("-updated_at")
                            .values("progress")[:1]
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
        """Возвращает класс сериализатора в зависимости от текущего действия."""
        if self.action == "complete":
            return None
        return LessonSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Получает детали урока, активируя его для пользователя при необходимости.

        Возвращает:

                200: Успешный ответ
                404: Урок не найден
        """
        lesson = self.get_object()
        user = self.request.user
        course = lesson.chapter.course
        if user.is_authenticated:
            try:
                subscription = Subscription.objects.get(course=course, user=user)
            except Subscription.DoesNotExist:
                raise SubscriptionDoesNotExist()
            any_progress = LessonProgressStatus.objects.filter(subscription=subscription, lesson=lesson).exists()
            if not any_progress:
                lesson.activate(subscription)
        if subscription and subscription.status == Subscription.Status.ENROLLED:
            course.activate(subscription)  # Активируем начало прохождения курса, если были записаны на курс
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    @action(
        detail=True,
        methods=["post"],
        permission_classes=(
            IsAuthenticated,
            IsUserOrReadOnly,
            EnrolledAndCourseHasStarted,
        ),
    )
    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: "Урок успешно завершен",
            status.HTTP_404_NOT_FOUND: "Урок не найден",
        }
    )
    def complete(self, request, **kwargs):
        """
        Действие для завершения урока для конкретного пользователя.

        Возвращает:
            - Response: Ответ, указывающий на успешное завершение урока (HTTP 201 Created).

        Примечание:
            Для выполнения данного действия требуется аутентификация пользователя.
            Урок завершается с использованием метода `finish`, который выполняет
            необходимые действия по завершению урока для конкретного пользователя.
        """
        user = self.request.user
        lesson = get_object_or_404(Lesson, **kwargs)
        subscription = get_object_or_404(Subscription, user=user, course=lesson.chapter.course)
        lesson.finish(subscription)
        return Response(status=status.HTTP_201_CREATED)


class FilterListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Класс представления для просмотра списка фильтров.

    Предоставляет возможность только для чтения (ReadOnly).

    Атрибуты:
        - queryset: Коллекция уровней, используемая для формирования списка фильтров.
    """

    queryset = [Level]
    serializer_class = FilterSerializer

from django.db.models import F
from rest_framework import serializers

from lizaalert.courses.models import Lesson, LessonProgressStatus


class CourseBreadcrumbSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class ChapterBreadcrumbSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class BreadcrumbSchema(serializers.Serializer):
    """Schema serializer for OpenAPI/Swagger."""

    course = CourseBreadcrumbSerializer()
    chapter = ChapterBreadcrumbSerializer()


class BreadcrumbLessonSerializer(serializers.Serializer):
    """Schema serializer for OpenAPI/Swagger."""

    chapter_id = serializers.IntegerField()
    lesson_id = serializers.IntegerField()


def current_lesson_queryset_getter(course, user):
    """
    Вернуть queryset для аннотации текущего урока.

    Функция возвращает queryset для текущего урока пользователя в следующем порядке:
    1. Текущий урок со статутсом отличным от FINISHED, если нет то
    2. Текущий урок следующий после статуса FINISHED, если нет то
    3. Первый урок курса.
    """
    ordered_lessons = (
        Lesson.objects.filter(chapter__course=course)
        .annotate(ordering=F("chapter__order_number") + F("order_number"))
        .order_by("ordering")
    )
    current_lesson_queryset = ordered_lessons.filter(
        chapter__course=course, status=Lesson.LessonStatus.PUBLISHED, lesson_progress__user=user
    ).exclude(lesson_progress__userlessonprogress=LessonProgressStatus.ProgressStatus.FINISHED)
    check_exists = current_lesson_queryset.exists()

    if not check_exists:
        last_finished = (
            ordered_lessons.filter(
                chapter__course=course,
                status=Lesson.LessonStatus.PUBLISHED,
                lesson_progress__user=user,
                lesson_progress__userlessonprogress=LessonProgressStatus.ProgressStatus.FINISHED,
            )
            .order_by("-ordering")
            .values("ordering")
            .first()
        )
        if last_finished:
            return ordered_lessons.filter(
                chapter__course=course, status=Lesson.LessonStatus.PUBLISHED, ordering__gt=last_finished["ordering"]
            )

    if not check_exists and not last_finished:
        return ordered_lessons.filter(chapter__course=course, status=Lesson.LessonStatus.PUBLISHED)
    return current_lesson_queryset

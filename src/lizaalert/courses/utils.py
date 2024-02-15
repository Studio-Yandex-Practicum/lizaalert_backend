import functools

from rest_framework import serializers

from lizaalert.courses.exceptions import ProgressNotFinishedException
from lizaalert.homeworks.models import ProgressionStatus


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


def check_finished_content(lesson_type=()):
    """
    Проверка завершения контента урока.

    В кортеж lesson_type передаются типы уроков, для которых необходимо проверить завершение контента.
    Если тип урока имеет обязательный контент, то необходимо проверить, что контент пройден.
    """

    def decorator_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lesson = args[0]
            subscription = args[1]
            if lesson.lesson_type in lesson_type:
                approved = (
                    getattr(lesson, lesson.lesson_type.lower())
                    .filter(subscription=subscription, status=ProgressionStatus.APPROVED, required=True)
                    .exists()
                )
                if not approved:
                    raise ProgressNotFinishedException("Необходимый контент урока не пройден.")
            return func(*args, **kwargs)

        return wrapper

    return decorator_func

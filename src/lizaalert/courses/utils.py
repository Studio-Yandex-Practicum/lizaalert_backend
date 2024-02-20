from rest_framework import serializers

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


def check_finished_content(lesson, subscription, lesson_type=None):
    """
    Проверка завершения контента урока.

    В кортеж lesson_type передаются типы уроков, для которых необходимо проверить завершение контента.
    Если тип урока имеет обязательный контент, то необходимо проверить, что контент пройден.
    """
    if lesson.lesson_type in lesson_type:
        return (
            getattr(lesson, lesson.lesson_type.lower())
            .filter(subscription=subscription, status=ProgressionStatus.APPROVED, required=True)
            .exists()
        )
    return True

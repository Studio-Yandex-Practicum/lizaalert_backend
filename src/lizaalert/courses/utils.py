from django.shortcuts import get_object_or_404
from rest_framework import serializers

from lizaalert.courses.exceptions import BadRequestException


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


def get_object(model, message="Invalid id.", **kwargs):
    """Проверить корректность введенного id."""
    try:
        return get_object_or_404(model, **kwargs)
    except ValueError:
        raise BadRequestException({"detail": message})

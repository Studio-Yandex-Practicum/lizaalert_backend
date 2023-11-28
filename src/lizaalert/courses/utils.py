from rest_framework import serializers

LESSON_STEP = 10


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


class ErrorSerializer(serializers.Serializer):
    """Schema error serializer for OpenAPI/Swagger."""

    error = serializers.CharField()

from django.utils import timezone
from rest_framework import serializers

from lizaalert.courses.models import Subscription


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


class UserStatusBreadcrumbSerializer(BreadcrumbLessonSerializer):
    """Schema serializer for OpenAPI/Swagger."""

    user_status = serializers.SerializerMethodField()

    def get_user_status(self, obj):
        if obj["user_status"].status == Subscription.Status.ENROLLED and check_course_available(
            obj["user_status"].course
        ):
            return Subscription.Status.AVAILABLE
        return obj["user_status"].status


class ErrorSerializer(serializers.Serializer):
    """Schema error serializer for OpenAPI/Swagger."""

    detail = serializers.CharField()


def check_course_available(course):
    """Проверить доступность курса."""
    return timezone.now().date() >= course.start_date

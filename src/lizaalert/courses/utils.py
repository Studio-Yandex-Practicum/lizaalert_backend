from drf_yasg.utils import swagger_serializer_method
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

    @swagger_serializer_method(serializer_or_field=serializers.ChoiceField(choices=Subscription.Status.choices))
    def get_user_status(self, obj):
        if obj["user_status"].status == Subscription.Status.ENROLLED and obj["user_status"].course.is_available:
            return Subscription.Status.AVAILABLE
        return obj["user_status"].status

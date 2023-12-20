from rest_framework import serializers


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

    user_status = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    """Schema error serializer for OpenAPI/Swagger."""

    detail = serializers.CharField()


def update_subscriptions(user):
    """Обновить статусы подписок пользователя."""
    try:
        subscriptions = user.subscriptions.all()
        for subscription in subscriptions:
            subscription.update_status()
    except Exception:
        pass


def update_one_subscription(user, course):
    """Обновить статус одной подписки пользователя."""
    try:
        subscription = user.subscriptions.get(course=course)
        subscription.update_status()
    except Exception:
        pass

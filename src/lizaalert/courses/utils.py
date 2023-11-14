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


def old_order_number_getter(instance):
    """Получить старый порядковый номер."""
    if instance.id:
        old_instance = type(instance).objects.get(id=instance.id)
        instance._old_order_number = old_instance.order_number
    else:
        instance._old_order_number = None

from django.db.models import Max
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


class HideOrderNumberMixin:
    """
    Убирает поле order_number при создании, оставляет при редактировании.

    Логика создания нумерации поля order_number не очевидна, поэтому при
    создании порядка данный механизм скрыт от администратора. При редактировании
    объекта администратору показаывается нумерация и появляется возможность поменять
    порядок.
    """

    field = "order_number"

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj and self.field:
            return [field for field in fields if field != self.field]
        return fields


def set_ordering(self, queryset, order_factor, chapter_order=None):
    if not self.id:
        max_order_number = queryset.aggregate(Max("order_number")).get("order_number__max")
        current_order = chapter_order if chapter_order else 0
        self.order_number = (max_order_number or current_order) + order_factor
    else:
        if hasattr(self, "_old_order_number") and self._old_order_number != self.order_number:
            objects = queryset.order_by("order_number")
            current_order = chapter_order if chapter_order else 0
            for position, object in enumerate(objects):
                object.order_number = (position + 1) * order_factor + current_order
            queryset.model.objects.bulk_update(objects, ["order_number"])

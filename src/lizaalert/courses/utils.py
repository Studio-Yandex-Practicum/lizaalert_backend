from django.db.models import Max
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
    """
    Устанавливает очередность глав и уроков.

    self - глава/урок
    queryset - вызываем объект более высокого уровня
    order_factor - номер порядка, 1000 или 10
    chapter_order - default None, порядковый номер главы, вызывается только если функция
    применяется для Урока.
    """
    if not self.id:
        max_order_number = queryset.aggregate(Max("order_number")).get("order_number__max")
        current_order = chapter_order if chapter_order else 0
        self.order_number = (max_order_number or current_order) + order_factor


def reset_ordering(self, queryset, order_factor, chapter_order=None):
    """
    Переустанавливает очередность глав и уроков.

    self - глава/урок
    queryset - вызываем объект более высокого уровня
    order_factor - номер порядка, 1000 или 10
    chapter_order - default None, порядковый номер главы, вызывается только если функция
    применяется для Урока.
    """
    if hasattr(self, "_old_order_number") and self._old_order_number != self.order_number:
        objects = queryset.order_by("order_number")
        current_order = chapter_order if chapter_order else 0
        for position, object in enumerate(objects):
            object.order_number = (position + 1) * order_factor + current_order
        queryset.model.objects.bulk_update(objects, ["order_number"])

        # При изменении порядка в глав в курсе, триггерим изменение одного урока в каждой главе,
        # чтобы произошел пересчет порядковых номеров.
        if not chapter_order:
            from lizaalert.courses.models import Chapter, Lesson

            chapters = Chapter.objects.filter(course=self.course)
            for chapter in chapters:
                try:
                    first_lesson = Lesson.objects.filter(chapter=chapter).order_by("order_number").first()
                    first_lesson.order_number = self.order_number + LESSON_STEP
                    first_lesson.save()
                except AttributeError:
                    pass


def old_order_number_getter(instance):
    """Получить старый порядковый номер."""
    if instance.id:
        old_instance = type(instance).objects.get(id=instance.id)
        instance._old_order_number = old_instance.order_number
    else:
        instance._old_order_number = None

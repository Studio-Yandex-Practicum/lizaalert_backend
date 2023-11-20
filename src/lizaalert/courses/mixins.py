from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Max

from lizaalert.courses.exceptions import WrongMethodException


class TimeStampedModel(models.Model):
    """
    Абстрактная модель времени создания или изменения данных.

    created_at* - дата создания записи об уроке, автоматическое проставление
    текущего времени
    updated_at* - дата обновления записи об уроке, автоматическое проставление
    текущего времени.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


def order_number_mixin(step, parent_field):
    """Order number mixin setter."""

    class SaveOrderingMixin(models.Model):
        """Ordering mixin."""

        class Meta:
            abstract = True

        order_number = models.PositiveSmallIntegerField(
            verbose_name="порядковый номер", validators=[MinValueValidator(1)], blank=True
        )

        @property
        def order_queryset(self):
            """Queryset for ordering."""
            cls = type(self)
            filter_params = {parent_field: getattr(self, parent_field)}
            return cls.objects.filter(**filter_params)

        def set_ordering(self, queryset, order_factor):
            """
            Устанавливает очередность глав и уроков.

            self - глава/урок
            queryset - вызываем объект более высокого уровня
            order_factor - номер порядка, 1000 или 10.
            """
            if not self.id:
                max_order_number = queryset.aggregate(Max("order_number")).get("order_number__max")
                self.order_number = (max_order_number or 0) + order_factor

        def reset_ordering(self, queryset, order_factor):
            """
            Переустанавливает очередность глав и уроков.

            self - глава/урок
            queryset - вызываем объект более высокого уровня
            order_factor - номер порядка, 1000 или 10.
            """
            if hasattr(self, "_old_order_number") and self._old_order_number != self.order_number:
                objects = queryset.order_by("order_number")
                for position, object in enumerate(objects):
                    object.order_number = (position + 1) * order_factor
                queryset.model.objects.bulk_update(objects, ["order_number"])

        def save(self, *args, **kwargs):
            """Change ordering method."""
            check_for_update = kwargs.get("update_fields", None)
            if (self.id and check_for_update is None) or (
                check_for_update is not None and "order_number" in check_for_update
            ):
                super().save(*args, **kwargs)
                self.reset_ordering(self.order_queryset, step)
            else:
                self.set_ordering(self.order_queryset, step)
                super().save(*args, **kwargs)

        @property
        def ordered(self):
            """Вернуть очередность всех уроков курса с полем ordering."""
            if parent_field == "chapter":
                cls = type(self)
                return (
                    cls.objects.filter(chapter__course=self.chapter.course)
                    .annotate(ordering=F("chapter__order_number") + F("order_number"))
                    .order_by("ordering")
                )
            raise WrongMethodException

        @property
        def next_lesson(self):
            """Вернуть следующий по очереди урок."""
            if parent_field == "chapter":
                ordered_lessons = self.ordered
                return ordered_lessons.filter(ordering__gt=self.ordering).order_by("ordering").values("id")[:1]
            raise WrongMethodException

        @property
        def prev_lesson(self):
            """Вернуть предыдущий по очереди урок."""
            if parent_field == "chapter":
                ordered_lessons = self.ordered
                return ordered_lessons.filter(ordering__lt=self.ordering).order_by("-ordering").values("id")[:1]
            raise WrongMethodException

        @classmethod
        def old_order_number_getter(cls, instance):
            """Получить старый порядковый номер."""
            if instance.id:
                old_instance = type(instance).objects.get(id=instance.id)
                instance._old_order_number = old_instance.order_number
            else:
                instance._old_order_number = None

    return SaveOrderingMixin

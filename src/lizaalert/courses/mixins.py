from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Max


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

        @property
        def parent_order(self):
            # родительский объект, у которого есть order_number
            """Chapter order for further ordering."""
            # try:
            #     return getattr(getattr(self, parent_field), "order_number")
            # except AttributeError:
            #     return None
            return getattr(getattr(self, parent_field), "order_number", None)

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
                            first_lesson.order_number = self.order_number + step
                            first_lesson.save()
                        except AttributeError:
                            pass

        def save(self, *args, **kwargs):
            """Change ordering method."""
            check_for_update = kwargs.get("update_fields", None)
            if (self.id and check_for_update is None) or (
                check_for_update is not None and "order_number" in check_for_update
            ):
                super().save(*args, **kwargs)
                self.reset_ordering(self.order_queryset, step, self.parent_order)
            else:
                self.set_ordering(self.order_queryset, step, self.parent_order)
                super().save(*args, **kwargs)

    return SaveOrderingMixin

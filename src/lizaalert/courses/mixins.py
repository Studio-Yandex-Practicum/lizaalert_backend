from django.core.validators import MinValueValidator
from django.db import models

from lizaalert.courses.utils import reset_ordering, set_ordering


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
            return list(filter(lambda f: f != self.field, fields))
        return fields


def order_number_mixin(step, name_of_instance):
    """Order number mixin setter."""
    class SaveOrderingMixin(models.Model):
        """Ordering mixin."""

        class Meta:
            abstract = True

        order_number = models.PositiveSmallIntegerField(
            verbose_name=f"порядковый номер {name_of_instance}", validators=[MinValueValidator(1)], blank=True
        )

        @property
        def chapter_order(self):
            return None

        def save(self, *args, **kwargs):
            """Change ordering method."""
            check_for_update = kwargs.get("update_fields", None)
            if (self.id and check_for_update is None) or (
                check_for_update is not None and "order_number" in check_for_update
            ):
                super().save(*args, **kwargs)
                reset_ordering(self, self.order_queryset, step, self.chapter_order)
            else:
                set_ordering(self, self.order_queryset, step, self.chapter_order)
                super().save(*args, **kwargs)
    return SaveOrderingMixin

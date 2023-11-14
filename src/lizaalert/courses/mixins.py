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


def order_number_mixin(step, parent_field, name_of_instance):
    """Order number mixin setter."""

    class SaveOrderingMixin(models.Model):
        """Ordering mixin."""

        class Meta:
            abstract = True

        order_number = models.PositiveSmallIntegerField(
            verbose_name=f"порядковый номер {name_of_instance}", validators=[MinValueValidator(1)], blank=True
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
            try:
                return getattr(getattr(self, parent_field), "order_number")
            except AttributeError:
                return None

        def save(self, *args, **kwargs):
            """Change ordering method."""
            check_for_update = kwargs.get("update_fields", None)
            if (self.id and check_for_update is None) or (
                check_for_update is not None and "order_number" in check_for_update
            ):
                super().save(*args, **kwargs)
                reset_ordering(self, self.order_queryset, step, self.parent_order)
            else:
                set_ordering(self, self.order_queryset, step, self.parent_order)
                super().save(*args, **kwargs)

    return SaveOrderingMixin

from django.core.validators import MinValueValidator
from django.db import models


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


def order_number_mixin(name_of_instance):
    """Order number mixin setter."""

    class OrderNumberMixin(models.Model):
        """Order number mixin."""

        class Meta:
            abstract = True

        order_number = models.PositiveSmallIntegerField(
            verbose_name=f"порядковый номер {name_of_instance}", validators=[MinValueValidator(1)], blank=True
        )

    return OrderNumberMixin

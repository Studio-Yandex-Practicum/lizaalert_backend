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
            old_order_number = type(self).objects.get(id=self.id)
            if old_order_number != self.order_number:
                objects = queryset.order_by("order_number")
                for position, object in enumerate(objects):
                    object.order_number = (position + 1) * order_factor
                queryset.model.objects.bulk_update(objects, ["order_number"])

        def _set_ordering(self, queryset, order_factor):
            """
            Установить/переустановить очередность глав и уроков.

            self - глава/урок
            queryset - вызываем объект более высокого уровня
            order_factor - номер порядка, 1000 или 10.
            """
            if not self.id:
                max_order_number = queryset.aggregate(Max("order_number")).get("order_number__max")
                self.order_number = (max_order_number or 0) + order_factor
                return self.order_number

            # получаем старый порядковый номер
            old_order_number = type(self).objects.filter(id=self.id).values("order_number").first()
            # округляем новый порядковый номер до шага очередности
            if self.order_number % order_factor != 0:
                rounded_new_order_number = (self.order_number // order_factor + 1) * order_factor
            else:
                rounded_new_order_number = self.order_number
            if old_order_number["order_number"] != self.order_number:
                objects = queryset.exclude(id=self.id).order_by("order_number")
                objects_to_update = []
                modifier_flag = False
                # for position, object in enumerate(objects):
                #     if modifier_flag:
                #         object.order_number = (position + 2) * order_factor
                #         objects_to_update.append(object)

                #     # переносим все последующие уроки на один шаг вперед
                #     elif object.order_number == rounded_new_order_number:
                #         object.order_number = (position + 2) * order_factor
                #         modifier_flag = True
                #         objects_to_update.append(object)

                #     # если есть окно, заполняем его уроками
                #     elif (position + 1) * order_factor != object.order_number:
                #         object.order_number = (position + 1) * order_factor
                #         objects_to_update.append(object)
                position = order_factor
                anchor = 0
                while objects:
                    obj = objects[anchor]
                    if modifier_flag:
                        obj.order_number = position
                        objects_to_update.append(obj)

                    # переносим все последующие уроки на один шаг вперед
                    elif obj.order_number == rounded_new_order_number:
                        position += order_factor
                        obj.order_number = position
                        modifier_flag = True
                        objects_to_update.append(obj)

                    # если есть окно, заполняем его уроками
                    elif position != obj.order_number:
                        obj.order_number = position
                        objects_to_update.append(obj)

                    position += order_factor
                    anchor += 1
                    if anchor >= len(objects):
                        break
                if modifier_flag:
                    self.order_number = rounded_new_order_number
                else:
                    # если менялся только порядок последнего урока, то назначаем номер от последнего-1 урока
                    if objects_to_update:
                        max_order_number = max(obj.order_number for obj in objects_to_update)
                    else:
                        max_order_number = max(obj.order_number for obj in objects)
                    self.order_number = max_order_number + order_factor
                queryset.model.objects.bulk_update(objects_to_update, ["order_number"])
            return self.order_number

        def save(self, *args, **kwargs):
            """Change ordering method."""
            self._set_ordering(self.order_queryset, step)
            # if not self.id:
            #     self.set_ordering(self.order_queryset, step)
            # else:
            #     self.reset_ordering(self.order_queryset, step)
            super().save(*args, **kwargs)

    return SaveOrderingMixin

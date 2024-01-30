from django.apps import apps
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
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
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
                self.order_number = (self.order_number // order_factor + 1) * order_factor
            if old_order_number["order_number"] != self.order_number:
                objects = queryset.exclude(id=self.id).order_by("order_number")
                objects_to_update = []
                position = order_factor
                for obj in objects:
                    # переносим все последующие уроки на один шаг вперед
                    if obj.order_number == self.order_number:
                        position += order_factor

                    # если есть окно, заполняем его уроками
                    if position != obj.order_number:
                        obj.order_number = position
                        objects_to_update.append(obj)
                    position += order_factor
                if self.order_number > position:
                    self.order_number = position
                queryset.model.objects.bulk_update(objects_to_update, ["order_number"])
            return self.order_number

        def save(self, *args, **kwargs):
            """Change ordering method."""
            self._set_ordering(self.order_queryset, step)
            super().save(*args, **kwargs)

    return SaveOrderingMixin


def status_update_mixin(parent: str = None, publish_status=None):
    """Добавить методы finish и activate для обновления статусов модели. При необходимости обновить подписку."""
    from lizaalert.courses.models import BaseProgress

    class FinishActivateMixin(models.Model):
        class Meta:
            abstract = True

        def _get_progress_model(self):
            """Получить модель прогресса путем конканектации имени модели и ProgressStatus."""
            model_name = f"{self.__class__.__name__}ProgressStatus"
            return apps.get_model("courses", model_name)

        def _update_or_create_progress_status(self, subscription, instance, status):
            """Обновление статуса прохождения урока, главы, курса, а также статуса подписки."""
            lookup_field = self.__class__.__name__.lower()
            model = self._get_progress_model()
            progress_status, created = model.objects.get_or_create(
                subscription=subscription, **{lookup_field: instance}, defaults={"progress": status}
            )
            if not created:
                setattr(progress_status, "progress", status)
                progress_status.save()

        def finish(self, subscription):
            """Присвоить статус завершения."""
            self._update_or_create_progress_status(
                subscription,
                self,
                BaseProgress.ProgressStatus.FINISHED,
            )

            if parent:
                filter_kwargs = {f"{self.__class__.__name__.lower()}__{parent}": getattr(self, parent)}
                finished_queryset = (
                    self._get_progress_model()
                    .objects.filter(
                        subscription=subscription, progress=BaseProgress.ProgressStatus.FINISHED, **filter_kwargs
                    )
                    .values(f"{self.__class__.__name__.lower()}_id")
                )

                filter_args = {parent: getattr(self, parent)}
                if publish_status:
                    filter_args["status"] = getattr(self, publish_status).PUBLISHED

                items = self.__class__.objects.filter(**filter_args).exclude(id__in=finished_queryset).count()

                if items == 0:
                    getattr(getattr(self, parent), "finish")(subscription)

        def activate(self, subscription):
            """Присвоить статус активировать."""
            self._update_or_create_progress_status(
                subscription,
                self,
                BaseProgress.ProgressStatus.ACTIVE,
            )

    return FinishActivateMixin

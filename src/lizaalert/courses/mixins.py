from dataclasses import dataclass

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


class ProgressMixin(models.Model):
    """Progress mixin."""

    class ProgressStatus(models.IntegerChoices):
        """класс по определению статуса прохождения урока, главы, курса, возможно тестов."""

        NOTSTARTED = 0, "Не начат"
        ACTIVE = 1, "Начат"
        FINISHED = 2, "Пройден"

    class Meta:
        abstract = True


@dataclass
class StatusConfig:
    model: any
    model_field: str
    finish_status: int
    active_status: int
    lookup_field: str
    subscription_model: any = None
    subscription_field: str = None
    subscription_active_status: any = None
    subscription_finish_status: any = None


def status_update_mixin():
    """Добавить методы finish и activate для обновления статусов модели. При необходимости обновить подписку."""

    def _get_config(model):
        if model == "course":
            from lizaalert.courses.models import CourseProgressStatus, Subscription

            return StatusConfig(
                CourseProgressStatus,
                "usercourseprogress",
                CourseProgressStatus.ProgressStatus.FINISHED,
                CourseProgressStatus.ProgressStatus.ACTIVE,
                "course",
                Subscription,
                "status",
                Subscription.Status.IN_PROGRESS,
                Subscription.Status.COMPLETED,
            )
        if model == "chapter":
            from lizaalert.courses.models import ChapterProgressStatus, Subscription

            return StatusConfig(
                ChapterProgressStatus,
                "userchapterprogress",
                ChapterProgressStatus.ProgressStatus.FINISHED,
                ChapterProgressStatus.ProgressStatus.ACTIVE,
                "chapter",
            )
        if model == "lesson":
            from lizaalert.courses.models import LessonProgressStatus, Subscription

            return StatusConfig(
                LessonProgressStatus,
                "userlessonprogress",
                LessonProgressStatus.ProgressStatus.FINISHED,
                LessonProgressStatus.ProgressStatus.ACTIVE,
                "lesson",
            )
        raise ValueError(f"Unknown model {model}")

    class FinishActivateMixin(models.Model):
        class Meta:
            abstract = True

        def _update_or_create_progress_status(self, model, user, instance, field, status, lookup_field):
            """Обновление статуса прохождения урока, главы, курса, а также статуса подписки."""
            progress_status, created = model.objects.get_or_create(
                user=user, **{lookup_field: instance}, defaults={field: status}
            )
            if not created:
                setattr(progress_status, field, status)
                progress_status.save()

        def finish(self, user):
            """Присвоить статус завершения."""
            status_config = _get_config(self.__class__.__name__.lower())
            self._update_or_create_progress_status(
                status_config.model,
                user,
                self,
                status_config.model_field,
                status_config.finish_status,
                status_config.lookup_field,
            )
            if status_config.subscription_model:
                self._update_or_create_progress_status(
                    status_config.subscription_model,
                    user,
                    self,
                    status_config.subscription_field,
                    status_config.subscription_finish_status,
                    status_config.lookup_field,
                )

        def activate(self, user):
            """Присвоить статус активировать."""
            status_config = _get_config(self.__class__.__name__.lower())
            self._update_or_create_progress_status(
                status_config.model,
                user,
                self,
                status_config.model_field,
                status_config.active_status,
                status_config.lookup_field,
            )
            if status_config.subscription_model:
                self._update_or_create_progress_status(
                    status_config.subscription_model,
                    user,
                    self,
                    status_config.subscription_field,
                    status_config.subscription_active_status,
                    status_config.lookup_field,
                )

    return FinishActivateMixin

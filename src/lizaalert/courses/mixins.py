from django.db import models, transaction


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


class ActivateLessonMixin(models.Model):
    """Абстрактная модель активации прохождения урока."""

    class Meta:
        abstract = True

    @transaction.atomic
    def activate(self, user):
        """Активировать урок."""
        from lizaalert.courses.models import LessonProgressStatus

        progress = LessonProgressStatus.objects.get_or_create(user=user, lesson=self)
        progress[0].userlessonprogress = LessonProgressStatus.ProgressStatus.ACTIVE
        progress[0].save()

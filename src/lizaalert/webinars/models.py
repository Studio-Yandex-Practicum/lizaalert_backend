from django.db import models

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.homeworks.models import ProgressionStatus

WEBINAR_PROGRESS = (
    (ProgressionStatus.DRAFT, "Draft"),
    (ProgressionStatus.APPROVED, "APPROVED"),
)


class Webinar(TimeStampedModel):
    """
    Модель для вебинара.

    У модели есть 2 статуса прохождения.
    status - статус прохождения;
    урок - урок, к которому привязан вебинар;
    link - ссылка на вебинар;
    subscription - подписка, к которой привязан вебинар.
    """

    status = models.PositiveSmallIntegerField(
        verbose_name="Статус",
        choices=WEBINAR_PROGRESS,
        default=ProgressionStatus.DRAFT,
    )
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, verbose_name="Урок", related_name="webinar")
    link = models.CharField(verbose_name="Ссылка на вебинар", max_length=400)
    subscription = models.ForeignKey("courses.Subscription", on_delete=models.CASCADE, verbose_name="Подписка")
    webinar_date = models.DateTimeField(verbose_name="Дата вебинара")

    class Meta:
        verbose_name = "Вебинар"
        verbose_name_plural = "Вебинары"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Вебинар для урока {self.lesson} - от пользователя {self.subscription}"

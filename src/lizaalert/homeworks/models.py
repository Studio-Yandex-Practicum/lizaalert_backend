from django.db import models

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.users.models import User


class ProgressionStatus(models.IntegerChoices):
    DRAFT = 0, "Черновик"
    SUBMITTED = 1, "Отправлено"
    IN_REVIEW = 2, "На проверке"
    APPROVED = 3, "Одобрено"
    REJECTED = 4, "Возвращено на доработку"
    CANCELLED = 5, "Отменено"


class Homework(TimeStampedModel):
    """
    Модель формы домашнего задания.

    У модели есть 6 статусов прохождения.
    reviewer - проверяющий, может изменяться оперативно;
    status - статус прохождения;
    урок - урок, к которому привязано задание, у одного урока может быть только одно задание;
    text - текст задания на 10к символов;
    subscription - подписка, к которой привязано задание;
    required - обязательное задание или нет, по умолчанию обязательное.
    """

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewer",
        verbose_name="Проверяющий",
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус",
        choices=ProgressionStatus.choices,
        default=ProgressionStatus.DRAFT,
    )
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, verbose_name="Урок", related_name="homework")
    text = models.CharField(verbose_name="Текст задания", max_length=10000)
    subscription = models.ForeignKey("courses.Subscription", on_delete=models.CASCADE, verbose_name="Подписка")
    required = models.BooleanField(verbose_name="Обязательное задание", default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscription", "lesson"],
                name="unique_subscription_lesson",
            ),
        ]
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Домашняя работа для урока {self.lesson} - от пользователя {self.subscription}"

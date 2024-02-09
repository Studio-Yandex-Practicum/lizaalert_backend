from django.db import models

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.courses.models import Lesson, Subscription
from lizaalert.users.models import User


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

    class ProgressionStatus(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        SUBMITTED = 1, "Отправлено"
        IN_REVIEW = 2, "На проверке"
        APPROVED = 3, "Одобрено"
        REJECTED = 4, "Отклонено"
        CANCELLED = 5, "Отменено"

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewer",
        verbose_name="Проверяющий",
    )
    status = models.IntegerField(
        verbose_name="Статус", choices=ProgressionStatus.choices, default=ProgressionStatus.DRAFT
    )
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, verbose_name="Урок")
    text = models.CharField(verbose_name="Текст задания", max_length=10000)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, verbose_name="Подписка")
    required = models.BooleanField(verbose_name="Обязательное задание", default=True)

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Домашняя работа для урока {self.lesson} - от пользователя {self.subscription}"

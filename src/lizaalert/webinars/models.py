from django.db import models
from django.utils import timezone

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.settings.constants import DEFAULT_WEBINAR_LENGTH


class Webinar(TimeStampedModel):
    """
    Модель для создания вебинара.

    урок - урок, к которому привязан вебинар;
    link - ссылка на вебинар;
    когорта - когорта, к которой привязан вебинар.
    """

    class Status(models.IntegerChoices):
        COMING = 0, "Запланирован"
        FINISHED = 1, "Завершен"

    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, verbose_name="Урок", related_name="webinar")
    description = models.TextField(verbose_name="Описание вебинара", blank=True, null=True)
    link = models.URLField(verbose_name="Ссылка на вебинар", max_length=400, blank=True, null=True)
    recording_link = models.URLField(verbose_name="Запись вебинара", max_length=400, blank=True, null=True)
    recording_description = models.TextField(verbose_name="Описание записи вебинара", blank=True, null=True)
    cohort = models.ForeignKey(
        "courses.Cohort", on_delete=models.CASCADE, verbose_name="Когорта", related_name="webinar"
    )
    webinar_date = models.DateTimeField(verbose_name="Дата вебинара")
    duration = models.PositiveSmallIntegerField(verbose_name="Длительность вебинара", default=DEFAULT_WEBINAR_LENGTH)

    class Meta:
        verbose_name = "Вебинар для когорты"
        verbose_name_plural = "Вебинары для когорты"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"<Lesson: {self.lesson_id}, Cohort: {self.cohort_id}>"

    @property
    def status(self):
        """
        Получение статуса прохождения вебинара.

        Если дата-время вебинара + предполагаемая длительность вебинара в минутах, меньше текущего времени,
        то вебинар считается завершенным, иначе - запланированным.
        """
        if (self.webinar_date + timezone.timedelta(minutes=self.duration)) <= timezone.now():
            return Webinar.Status.FINISHED
        return Webinar.Status.COMING

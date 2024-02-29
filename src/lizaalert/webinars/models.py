from django.db import models

from lizaalert.courses.mixins import TimeStampedModel


class Webinar(TimeStampedModel):
    """
    Модель для создания вебинара.

    урок - урок, к которому привязан вебинар;
    link - ссылка на вебинар;
    когорта - когорта, к которой привязан вебинар.
    """

    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, verbose_name="Урок", related_name="webinar")
    description = models.TextField(verbose_name="Описание вебинара", max_length=5000, blank=True, null=True)
    link = models.URLField(verbose_name="Ссылка на вебинар", max_length=400)
    cohort = models.ForeignKey(
        "courses.Cohort", on_delete=models.CASCADE, verbose_name="Когорта", related_name="webinar"
    )
    webinar_date = models.DateTimeField(verbose_name="Дата вебинара")

    class Meta:
        verbose_name = "Вебинар для когорты"
        verbose_name_plural = "Вебинары для когорты"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"<Lesson: {self.lesson_id}, Cohort: {self.cohort_id}>"
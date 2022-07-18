from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=120, verbose_name="Название курса")
    format = models.CharField(max_length=60, verbose_name="Формат курса")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала курса")
    cover_path = models.FileField(blank=True, null=True, verbose_name="Путь к обложке курса")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание курса")
    level = models.ForeignKey("users.Level", on_delete=models.PROTECT, verbose_name="Уровень", related_name="course")
    full_description = models.TextField(verbose_name="Полное описание курса")
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель курса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания курса")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения курса")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class CourseStatus(models.Model):
    class SlugStatus(models.TextChoices):
        ACTIVE = "active"
        COMPLETE = "complete"
        REGISTRATION = "registration"

    name = models.CharField("Статус курса", max_length=50, editable=False)
    slug = models.CharField(
        max_length=20,
        choices=SlugStatus.choices,
        default=SlugStatus.ACTIVE,
        editable=False
    )

    class Meta:
        db_table = "course_status"
        verbose_name = "Статус курса"
        verbose_name_plural = "Статус курсов"

    def __str__(self):
        return f"{self.slug}"

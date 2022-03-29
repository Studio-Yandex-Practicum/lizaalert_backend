from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Course(models.Model):
    title = models.CharField(
        max_length=120,
        verbose_name='Название курса'
    )
    format = models.CharField(
        max_length=60,
        verbose_name='Формат курса'
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата начала курса'
    )
    cover_path = models.FileField(
        blank=True,
        null=True,
        verbose_name='Путь к обложке курса'
    )
    short_description = models.CharField(
        max_length=120,
        verbose_name='Краткое описание курса'
    )
    full_description = models.TextField(
        verbose_name='Полное описание курса'
    )
    attempts_limit = models.SmallIntegerField(
        verbose_name='Количество попыток на прохождение курса',
        validators=[MinValueValidator(0),
                    MaxValueValidator(10)]
    )
    user_created = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Создатель курса'
    )
    created_at = models.DateTimeField(
        auto_now_add = True,
        verbose_name='Дата создания курса'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения курса'
    )
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
    
    def __str__(self):
        return self.title

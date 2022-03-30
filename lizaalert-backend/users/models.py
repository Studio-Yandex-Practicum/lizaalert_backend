from django.conf import settings
from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from phonenumber_field.modelfields import PhoneNumberField


class Level(models.Model):
    LEVELS = (
        ('Новичок', 'Новичок'),
        ('Бывалый',  'Бывалый'),
        ('Профессионал', 'Профессионал')
    )

    name = models.CharField(
        'Наименование уровня', max_length=20,
        choices=LEVELS
    )
    description = models.TextField(
        'Описание уровня и условия его достижения',
    )

    class Meta:
        db_table = 'levels'
        verbose_name = 'Уровень'
        verbose_name_plural = 'Уровни'

    def __str__(self):
        return f'{self.name}'


class VolunteerLevel(models.Model):
    volunteer = models.ForeignKey(
        'Volunteer', on_delete=models.CASCADE,
        related_name='volunteer_levels',
        verbose_name='Волонтер'
    )
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE,
        related_name='level_volunteers',
        verbose_name='Уровень'
    )
    confirmed = models.BooleanField(
        'Статус подтверждения уровня', default=False
    )
    who_confirmed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        blank=True, null=True, verbose_name='Кто подтвердил статус'
    )
    created_at = models.DateTimeField(
        'Дата создания', auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления', auto_now=True
    )

    class Meta:
        db_table = 'volunteers_levels'
        verbose_name = 'Уровень волонтера'
        verbose_name_plural = 'Уровни волонтеров'
        constraints = (
            models.UniqueConstraint(
                fields=('volunteer', 'level'),
                name='unique_volunteer_level'),
        )


class Location(models.Model):
    code = models.PositiveSmallIntegerField(
        'Код региона', blank=True, null=True
    )
    region = models.CharField(
        'Наименование региона', max_length=120
    )

    class Meta:
        db_table = 'locations'
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class Direction(models.Model):
    title = models.CharField(
        'Наименование направления', max_length=120
    )
    description = models.TextField(
        'Описание направления', blank=True, null=True
    )

    class Meta:
        db_table = 'directions'
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'

    def __str__(self):
        return f'{self.title}'


class Badge(models.Model):
    name = models.CharField(
        'Наименование значка', max_length=40
    )
    description = models.TextField(
        'Описание значка и условий его получения',
        blank=True, null=True
    )

    class Meta:
        db_table = 'badges'
        verbose_name = 'Значок'
        verbose_name_plural = 'Значки'

    def __str__(self):
        return f'{self.name}'


class VolunteerBadge(models.Model):
    volunteer = models.ForeignKey(
        'Volunteer', on_delete=models.CASCADE,
        related_name='volunteer_badges',
        verbose_name='Волонтер'
    )
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE,
        related_name='badge_volunteers',
        verbose_name='Значок'
    )
    created_at = models.DateTimeField(
        'Дата создания записи', auto_now_add=True
    )

    class Meta:
        db_table = 'volunteers_badges'
        verbose_name = 'Значок волонтера'
        verbose_name_plural = 'Значки волонтеров'


class Volunteer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    phone_number = PhoneNumberField(
        verbose_name='Номер телефона', unique=True
    )
    birth_date = models.DateField('Дата рождения')
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True,
        related_name='volunteers',
        verbose_name='Географический регион'
    )
    direction = models.ForeignKey(
        Direction, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='volunteers',
        verbose_name='Направление'
    )
    call_sign = models.CharField(
        'Позывной на форуме', max_length=50, blank=True, null=True
    )
    photo = ThumbnailerImageField(
        verbose_name='Путь к фотографии', blank=True, null=True
    )
    level = models.ManyToManyField(
        Level, through=VolunteerLevel, blank=True,
        related_name='volunteers',
        verbose_name='Уровень'
    )
    badges = models.ManyToManyField(
        Badge, through=VolunteerBadge, blank=True,
        related_name='volunteers',
        verbose_name='Значки'
    )
    created_at = models.DateTimeField(
        'Дата и время создания запси', auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления записи', auto_now=True
    )

    class Meta:
        db_table = 'volunteers'
        verbose_name = 'Волонтер'
        verbose_name_plural = 'Волонтеры'

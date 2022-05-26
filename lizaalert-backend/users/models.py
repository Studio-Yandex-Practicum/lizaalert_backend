from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    pass


class Level(models.Model):
    class LevelName(models.TextChoices):
        beginner = "Новичок", "Новичок"
        middle = "Бывалый", "Бывалый"
        professional = "Профессионал", "Профессионал"

    name = models.CharField("Наименование уровня", max_length=20, choices=LevelName.choices)
    description = models.TextField(
        "Описание уровня и условия его достижения",
    )

    class Meta:
        db_table = "levels"
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"

    def __str__(self):
        return f"{self.name}"


class VolunteerLevel(models.Model):
    volunteer = models.ForeignKey(
        "Volunteer", on_delete=models.CASCADE, related_name="volunteer_levels", verbose_name="Волонтер"
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="level_volunteers", verbose_name="Уровень")
    confirmed = models.BooleanField("Статус подтверждения уровня", default=False)
    who_confirmed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Кто подтвердил статус",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        db_table = "volunteers_levels"
        verbose_name = "Уровень волонтера"
        verbose_name_plural = "Уровни волонтеров"
        constraints = (models.UniqueConstraint(fields=("volunteer", "level"), name="unique_volunteer_level"),)


class Location(models.Model):
    code = models.PositiveSmallIntegerField("Код региона", blank=True, null=True)
    region = models.CharField("Наименование региона", max_length=120)

    class Meta:
        db_table = "locations"
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


class Department(models.Model):
    title = models.CharField("Наименование направления", max_length=120)
    description = models.TextField("Описание направления", blank=True, null=True)

    class Meta:
        db_table = "departments"
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self):
        return f"{self.title}"


class Badge(models.Model):
    name = models.CharField("Наименование значка", max_length=40)
    description = models.TextField("Описание значка и условий его получения", blank=True, null=True)

    class Meta:
        db_table = "badges"
        verbose_name = "Значок"
        verbose_name_plural = "Значки"

    def __str__(self):
        return f"{self.name}"


class VolunteerBadge(models.Model):
    volunteer = models.ForeignKey(
        "Volunteer", on_delete=models.CASCADE, related_name="volunteer_badges", verbose_name="Волонтер"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="badge_volunteers", verbose_name="Значок")
    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)

    class Meta:
        db_table = "volunteers_badges"
        verbose_name = "Значок волонтера"
        verbose_name_plural = "Значки волонтеров"


class VolunteerCourse(models.Model):
    class CourseStatuses(models.TextChoices):
        activ = "Активный"
        complete = "Пройден"
        registration = "Вы записаны"

    volunteer = models.ForeignKey(
        "Volunteer", on_delete=models.CASCADE, related_name="volunter_courses", verbose_name="Волонтер"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="course_volunteers", verbose_name="Курс"
    )
    status = models.ForeignKey("courses.CourseStatus", on_delete=models.PROTECT,
                               related_name="volunteer_courses", verbose_name="Статус")
    assessment = models.FloatField(
        "Оценка за курс", default=0.0, validators=(MinValueValidator(0.0), MaxValueValidator(100.0))
    )
    created_at = models.DateTimeField("Дата и время записи на курс", auto_now_add=True)

    class Meta:
        db_table = "volunteers_courses"
        verbose_name = "Курс волонтера"
        verbose_name_plural = "Курсы волонтеров"
        constraints = (
            models.UniqueConstraint(fields=("volunteer", "course", "status"), name="unique_volunteer_course"),
        )


class Volunteer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    phone_number = PhoneNumberField(verbose_name="Номер телефона", unique=True)
    birth_date = models.DateField("Дата рождения")
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name="volunteers", verbose_name="Географический регион"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="volunteers",
        verbose_name="Направление",
    )
    call_sign = models.CharField("Позывной на форуме", max_length=50, blank=True, null=True)
    photo = ThumbnailerImageField(verbose_name="Путь к фотографии", blank=True, null=True)
    level = models.ManyToManyField(
        Level, through=VolunteerLevel, blank=True, related_name="volunteers", verbose_name="Уровень"
    )
    badges = models.ManyToManyField(
        Badge, through=VolunteerBadge, blank=True, related_name="volunteers", verbose_name="Значки"
    )
    courses = models.ManyToManyField(
        "courses.Course", through=VolunteerCourse, blank=True, related_name="volunteers", verbose_name="Курсы"
    )
    created_at = models.DateTimeField("Дата и время создания запси", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления записи", auto_now=True)

    class Meta:
        db_table = "volunteers"
        verbose_name = "Волонтер"
        verbose_name_plural = "Волонтеры"

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_thumbnails.fields import ThumbnailerImageField
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Полное имя")
    phone = PhoneNumberField(max_length=20, null=True, blank=True, verbose_name="телефон")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("-id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UserRole(models.Model):
    """
    Роль пользователя.

    Отношение зарегистрированного пользователя и его роли в образовательной системе
    "ЛизаАлерт". Используется для разграничения прав доступа к учебным материалам.
    """

    class Role(models.TextChoices):
        MAIN_ADMIN = "main admin", "Главный Администратор"
        ADMIN = "admin", "Администратор"
        TEACHER = "teacher", "Преподаватель"
        VOLUNTEER = "volunteer", "Волонтёр"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField(choices=Role.choices, max_length=20, verbose_name="Роль пользователя")

    class Meta:
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"
        constraints = (models.UniqueConstraint(fields=("user", "role"), name="unique_user_role"),)

    def __str__(self) -> str:
        return f"{self.user} ({self.role})"


class Level(models.Model):
    class LevelName(models.TextChoices):
        beginner = "novice", "Новичок"
        middle = "experienced", "Бывалый"
        professional = "professional", "Профессионал"

    name = models.CharField(
        "Наименование уровня",
        max_length=20,
        choices=LevelName.choices,
        unique=True,
    )
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
        "Volunteer",
        on_delete=models.CASCADE,
        related_name="volunteer_levels",
        verbose_name="Волонтер",
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="level_volunteers",
        verbose_name="Уровень",
    )
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

    def __str__(self):
        return f"{self.region}"


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
    """Модель для создания значков."""

    class BadgeType(models.TextChoices):
        MANUAL = "manual", "Ручная"
        ACHIEVEMENT = "achievement", "За прохождение"

    class BadgeCategory(models.TextChoices):
        ONE_TIME = "one_time", "Разовая"
        PROGRESSIVE = "progressive", "За достижение"

    name = models.CharField("Наименование значка", max_length=40)
    description = models.TextField("Описание значка и условий его получения", blank=True, null=True)
    image = ThumbnailerImageField("Изображение значка", upload_to="badges/", blank=True, null=True)
    badge_type = models.CharField("Вид значка", choices=BadgeType.choices, max_length=20)
    badge_category = models.CharField("Тип значка", choices=BadgeCategory.choices, max_length=20)
    badge_slug = models.SlugField("Поле поиска", max_length=100, blank=True, null=True, unique=True)
    issued_for = models.CharField("За что", max_length=255)
    threshold_courses = models.PositiveIntegerField("Количество курсов для получения", null=True, blank=True)
    threshold_course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Курс для получения",
    )
    division = models.ForeignKey(
        "courses.Division", on_delete=models.PROTECT, verbose_name="Направление умения", null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("name", "division"), name="unique_badge"),
        ]
        db_table = "badges"
        verbose_name = "Значок"
        verbose_name_plural = "Значки"

    def __str__(self):
        return f"{self.name}"


class VolunteerBadge(models.Model):
    """Модель для представления значков волонтерам."""

    volunteer = models.ForeignKey(
        "Volunteer",
        on_delete=models.CASCADE,
        related_name="volunteer_badges",
        verbose_name="Волонтер",
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="badge_volunteers",
        verbose_name="Значок",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="course_volunteer_badge",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)

    class Meta:
        db_table = "volunteers_badges"
        verbose_name = "Значок волонтера"
        verbose_name_plural = "Значки волонтеров"


class VolunteerCourseCompletion(models.Model):
    volunteer = models.ForeignKey("Volunteer", on_delete=models.CASCADE, related_name="course_completion")
    completed_courses_count = models.PositiveIntegerField(default=0)


class VolunteerCourse(models.Model):
    volunteer = models.ForeignKey(
        "Volunteer",
        on_delete=models.CASCADE,
        related_name="volunter_courses",
        verbose_name="Волонтер",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="course_volunteers",
        verbose_name="Курс",
    )
    assessment = models.FloatField(
        "Оценка за курс",
        default=0.0,
        validators=(MinValueValidator(0.0), MaxValueValidator(100.0)),
    )
    created_at = models.DateTimeField("Дата и время записи на курс", auto_now_add=True)

    class Meta:
        db_table = "volunteers_courses"
        verbose_name = "Курс волонтера"
        verbose_name_plural = "Курсы волонтеров"
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "volunteer",
                    "course",
                ),
                name="unique_volunteer_course",
            ),
        )

    def __str__(self):
        return f"{self.volunteer.user} {self.course.title}"


class Volunteer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="volunteers",
        verbose_name="Географический регион",
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
        Level,
        through=VolunteerLevel,
        blank=True,
        null=True,
        related_name="volunteers",
        verbose_name="Уровень",
    )
    badges = models.ManyToManyField(
        Badge,
        through=VolunteerBadge,
        blank=True,
        null=True,
        related_name="volunteers",
        verbose_name="Значки",
    )
    courses = models.ManyToManyField(
        "courses.Course",
        through=VolunteerCourse,
        blank=True,
        related_name="volunteers",
        verbose_name="Курсы",
    )
    created_at = models.DateTimeField("Дата и время создания запси", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления записи", auto_now=True)

    class Meta:
        db_table = "volunteers"
        verbose_name = "Волонтер"
        verbose_name_plural = "Волонтеры"

    @property
    def level_confirmed(self):
        return self.volunteer_levels.filter(confirmed=True).order_by("-updated_at").first()

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def create_default_volunteer_level(sender, instance, created, **kwargs):
    if created:
        volunteer, created = Volunteer.objects.get_or_create(user=instance)
        beginner_level = Level.objects.filter(name=Level.LevelName.beginner).first()

        if beginner_level:
            existing_record = VolunteerLevel.objects.filter(volunteer=volunteer, level=beginner_level).exists()

            if not existing_record:
                VolunteerLevel.objects.create(volunteer=volunteer, level=beginner_level, confirmed=True)

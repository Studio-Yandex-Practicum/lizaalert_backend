from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class TimeStampedMixin(models.Model):
    """
    Абстрактная модель времени создания или изменения данных

    created_at* - дата создания записи об уроке, автоматическое проставление текущего времени
    updated_at* - дата обновления записи об уроке, автоматическое проставление текущего времени.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Course(TimeStampedMixin):
    title = models.CharField(max_length=120, verbose_name="Название курса")
    format = models.CharField(max_length=60, verbose_name="Формат курса")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала курса",
                                  validators=[MinValueValidator(limit_value=date.today)]
                                  )
    cover_path = models.FileField(blank=True, null=True, verbose_name="Путь к обложке курса")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание курса")
    level = models.ForeignKey("users.Level", on_delete=models.PROTECT, verbose_name="Уровень", related_name="course")
    full_description = models.TextField(verbose_name="Полное описание курса")
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель курса")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class CourseStatus(models.Model):
    name = models.CharField("Статус курса", max_length=50, editable=False)
    slug = models.SlugField(max_length=20, editable=False)

    class Meta:
        db_table = "course_status"
        verbose_name = "Статус курса"
        verbose_name_plural = "Статус курсов"

    def __str__(self):
        return f"{self.slug}"


class Lesson(TimeStampedMixin):
    """
    Модель урока.

    Поля модели:
    title* - название урока
    description - описание урока
    type* - тип урока, выбор из перечня Урок, Видеоурок, Вебинар, Тест (Квиз)
    tags - ключевые слова урока
    duration* - продолжительность урока, минут
    user_created* - пользователь создавший урок
    user_modified* - последний редактировавший урок
    lesson_status* - статус готовности урока (draft, ready, published)
    additional* - дополнительный урок - да/нет
    diploma* - дипломный урок - да/нет
    """

    class LessonType(models.TextChoices):
        LESSON = "Lesson", "Урок"
        VIDEOLESSON = "Videolesson", "Видеоурок"
        WEBINAR = "Webinar", "Вебинар"
        QUIZ = "Quiz", "Тест"

    class LessonStatus(models.TextChoices):
        DRAFT = "Draft", "В разработке"
        READY = "Ready", "Готов"
        PUBLISHED = "Published", "Опубликован"

    title = models.CharField(max_length=120, verbose_name="название урока")
    description = models.TextField(blank=True, null=True, verbose_name="описание урока")
    lesson_type = models.CharField(max_length=20, verbose_name="тип урока",
                                   choices=LessonType.choices)
    tags = models.CharField(max_length=255, verbose_name="ключевые слова урока")
    duration = models.PositiveSmallIntegerField(verbose_name="продолжительность урока")
    user_created = models.ForeignKey(User, related_name="lesson_creator", on_delete=models.PROTECT,
                                     verbose_name="пользователь, создавший урок")
    user_modifier = models.ForeignKey(User, related_name="lesson_editor", on_delete=models.PROTECT,
                                      verbose_name="пользователь, внёсший изменения в урок")
    lesson_status = models.CharField(max_length=20, verbose_name="статус урока", choices=LessonStatus.choices,
                                     default=LessonStatus.DRAFT)
    additional = models.BooleanField(verbose_name="дополнительный урок", default=False)
    diploma = models.BooleanField(verbose_name="дипломный урок", default=False)

    class Meta:
        ordering = ("title",)
        verbose_name = "урок"
        verbose_name_plural = "урок"

    def __str__(self):
        return self.title


class Chapter(TimeStampedMixin):
    """
    Модель главы.

    Поля модели:
    title - название главы
    lessons - уроки, входящие в главу
    user_created* - пользователь создавший главу
    user_modified* - пользователь последний редактировавший главу
    created_at* - дата создания записи о главе, автоматическое проставление текущего времени
    updated_at* - дата обновления записи о главе, автоматическое проставление текущего времени.
    """

    title = models.CharField(max_length=120, null=True, blank=True, verbose_name="название главы")
    lessons = models.ManyToManyField(Lesson, through='ChapterLesson', verbose_name="уроки главы")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name="Части", related_name="chapters")
    user_created = models.ForeignKey(User, related_name="chapter_creator", on_delete=models.PROTECT,
                                     verbose_name="пользователь, создавший главу")
    user_modifier = models.ForeignKey(User, related_name="chapter_editor", on_delete=models.PROTECT,
                                      verbose_name="пользователь, внёсший изменения в главу")

    class Meta:
        ordering = ("title",)
        verbose_name = "глава"
        verbose_name_plural = "глава"

    def __str__(self):
        return self.title


class ChapterLesson(models.Model):
    '''
    Модель связи глава-урок.

    Поля модели:
    chapter* - тип ForeignKey к модели главы урока Chapter
    lesson* - тип ForeignKey к модели курса Lesson
    order_number* - порядковый номер урока в главе >= 1
    created_at* - дата создания записи о связи глава-урок.
    '''

    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT)
    order_number = models.PositiveSmallIntegerField("порядковый номер урока в главе",
                                                    validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата добавления урока в главу")

    class Meta:
        ordering = ("chapter", "order_number")
        constraints = [
            models.UniqueConstraint(fields=["chapter", "lesson", "order_number"],
                                    name="unique_chapter_lesson")
        ]
        verbose_name = "Урок"
        verbose_name_plural = "Урок"

    def __str__(self):
        return f"{self.lesson.title}"

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.quizzes.models import Quiz

User = get_user_model()


class FAQ(TimeStampedModel):
    """
    Класс для хранения списка часто задаваемых вопросов.

    question - часто задаваемый вопрос
    answer - ответ на заданный вопрос
    created_at - дата создания вопроса
    updated_at - дата обновленя вопроса
    author - пользователь, создавший вопрос/ответ.
    """

    question = models.CharField(max_length=250, verbose_name="Вопрос")
    answer = models.CharField(max_length=1000, verbose_name="Ответ")
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель вопроса")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question


class Knowledge(TimeStampedModel):
    """
    Класс для хранения списка умений получаемых на курсе.

    title - название умения (уникальное значение)
    description - развернутое описание умения
    created_at - дата создания умения
    updated_at - дата обновленя умения
    author - пользователь, создавший умение.
    """

    title = models.CharField(max_length=250, verbose_name="Название умения")
    description = models.CharField(max_length=1000, verbose_name="Описание умения")
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель умения")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["title"], name="unique_knowledge")]
        verbose_name = "Умение"
        verbose_name_plural = "Умения"

    def __str__(self):
        return self.title


class Course(TimeStampedModel):
    title = models.CharField(max_length=120, verbose_name="Название курса")
    course_format = models.CharField(max_length=60, verbose_name="Формат курса")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала курса")
    cover_path = models.FileField(blank=True, null=True, verbose_name="Путь к обложке курса")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание курса")
    level = models.ForeignKey(
        "users.Level",
        on_delete=models.PROTECT,
        verbose_name="Уровень",
        related_name="course",
    )
    full_description = models.TextField(verbose_name="Полное описание курса")
    knowledge = models.ManyToManyField(Knowledge, through="CourseKnowledge", verbose_name="Умения", null=True)
    faq = models.ManyToManyField(FAQ, through="CourseFaq", verbose_name="Часто задаваемые вопросы", null=True)
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель курса")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return f"Course {self.title}"


class CourseStatus(models.Model):
    """
    Класс для хранения статуса курсов.

    Draft - курс находится в разработке, не готов к публикации.
    Published - курс готов, опубликован, пользователь может записаться на курс.
    Archive - курс готов, но снят с публикации, не виден пользователю.
    """

    class CourseStatusChoices(models.TextChoices):
        """Класс для выбора статуса курса."""

        DRAFT = "draft", "в разработке"
        PUBLISHED = "published", "опубликован"
        ARCHIVE = "archive", "в архиве"

    name = models.CharField("Статус курса", max_length=50, editable=False)
    slug = models.CharField("Слаг курса", max_length=50, editable=False)
    type_status = models.CharField(
        max_length=20,
        choices=CourseStatusChoices.choices,
        default=CourseStatusChoices.DRAFT,
        editable=False,
    )

    class Meta:
        db_table = "course_status"
        verbose_name = "Статус курса"
        verbose_name_plural = "Статус курсов"

    def __str__(self):
        return f"{self.slug} <{self.type_status}>"


class Chapter(TimeStampedModel):
    """
    Модель главы.

    Поля модели:
    title - название главы
    course - курс, к которому относится глава
    user_created* - пользователь создавший главу
    user_modified* - пользователь последний редактировавший главу
    created_at* - дата создания записи о главе, автоматическое проставление
    текущего времени
    updated_at* - дата обновления записи о главе, автоматическое проставление
    текущего времени.
    """

    title = models.CharField(max_length=120, null=True, blank=True, verbose_name="название главы")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс", related_name="chapters")
    user_created = models.ForeignKey(
        User,
        related_name="chapter_creator",
        on_delete=models.PROTECT,
        verbose_name="пользователь, создавший главу",
    )
    user_modifier = models.ForeignKey(
        User,
        related_name="chapter_editor",
        on_delete=models.PROTECT,
        verbose_name="пользователь, внёсший изменения в главу",
    )
    order_number = models.PositiveSmallIntegerField(
        verbose_name="порядковый номер главы", validators=[MinValueValidator(1)], default=1
    )

    class Meta:
        ordering = ("order_number",)
        verbose_name = "глава"
        verbose_name_plural = "глава"
        constraints = [
            models.UniqueConstraint(
                fields=["order_number", "course"],
                name="unique_order_number",
            )
        ]

    def __str__(self):
        return f"Курс {self.course.title}: Глава {self.title}"


class Lesson(TimeStampedModel):
    """
    Модель урока.

    Поля модели:
    title* - название урока
    chapter - глава, к которой относится курс
    description - описание урока
    lesson_type* - тип урока, выбор из перечня Урок, Видеоурок, Вебинар, Тест (Квиз)
    tags - ключевые слова урока
    duration* - продолжительность урока, минут
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
    chapter = models.ForeignKey(
        Chapter, on_delete=models.PROTECT, related_name="lessons", verbose_name="уроки главы", null=True
    )
    description = models.TextField(blank=True, null=True, verbose_name="описание урока")
    lesson_type = models.CharField(max_length=20, verbose_name="тип урока", choices=LessonType.choices)
    tags = models.CharField(max_length=255, verbose_name="ключевые слова урока")
    duration = models.PositiveSmallIntegerField(verbose_name="продолжительность урока")
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="квиз")
    user_created = models.ForeignKey(
        User,
        related_name="lesson_creator",
        on_delete=models.PROTECT,
        verbose_name="пользователь, создавший урок",
    )
    user_modifier = models.ForeignKey(
        User,
        related_name="lesson_editor",
        on_delete=models.PROTECT,
        verbose_name="пользователь, внёсший изменения в урок",
    )
    lesson_status = models.CharField(
        max_length=20, verbose_name="статус урока", choices=LessonStatus.choices, default=LessonStatus.DRAFT
    )
    additional = models.BooleanField(verbose_name="дополнительный урок", default=False)
    diploma = models.BooleanField(verbose_name="дипломный урок", default=False)
    order_number = models.PositiveSmallIntegerField(
        verbose_name="порядковый номер урока", validators=[MinValueValidator(1)], default=1
    )

    class Meta:
        ordering = ("order_number",)
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        constraints = [
            models.UniqueConstraint(
                fields=["order_number", "chapter"],
                name="unique_lesson_order_number",
            )
        ]

    def __str__(self):
        return f"Урок {self.id}: {self.title} (Глава {self.chapter_id})"


class LessonProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении уроков в главе и курсе. Наследуется от TimeStampedModel.

    Поля модели:

    lesson - тип ForeignKey к модели  Lesson
    user - тип ForeignKey к модели User
    lessonstatus - cтатус прохождения урока (в настоящий момент только finished)
    version_number - номер версии урока(предусматриваем для будующего использования, значение по умолчанию 1)
    """

    class ProgressStatus(models.TextChoices):
        """класс по определению статуса прохождения урока, главы, курса, возможно тестов."""

        COMING = 0, "Не начат"
        ACTIVE = 1, "Начат"
        FINISHED = 2, "Пройден"

    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="lesson_progress")
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_lesson_status",
        verbose_name="user_lesson_status",
    )
    userlessonprogress = models.CharField(
        max_length=20,
        verbose_name="прогресс урока",
        choices=ProgressStatus.choices,
    )
    version_number = models.PositiveSmallIntegerField("Номер версии урока", validators=[MinValueValidator(1)])

    def __str__(self):
        return f"Lesson {self.lesson.title}: {self.user.username}"


class ChapterProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении глав в курсе. Наследуется от TimeStampedModel.

    Поля модели:

    chapter - тип ForeignKey к модели  Chapter
    user - тип ForeignKey к модели User
    userchapterprogress - cтатус прохождения главы (в настоящий момент только finished).
    """

    class ProgressStatus(models.TextChoices):
        """класс по определению статуса прохождения урока, главы, курса, возможно тестов."""

        NOTSTARTED = 0, "Не начат"
        INPROGRESS = 1, "Начат"
        FINISHED = 2, "Пройден"

    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT, related_name="chapter_progress")
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_chapter_status",
        verbose_name="user_chapter_status",
    )
    userchapterprogress = models.CharField(
        max_length=20,
        verbose_name="прогресс главы",
        choices=ProgressStatus.choices,
    )


class CourseProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении глав в курсе. Наследуется от TimeStampedModel.

    Поля модели:

    chapter - тип ForeignKey к модели  Chapter
    user - тип ForeignKey к модели User
    usercourseprogress - cтатус прохождения курса (в настоящий момент только finished).
    """

    class ProgressStatus(models.TextChoices):
        """класс по определению статуса прохождения урока, главы, курса, возможно тестов."""

        NOTSTARTED = 0, "Не начат"
        INPROGRESS = 1, "Начат"
        FINISHED = 2, "Пройден"

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="course_progress")
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_course_status",
        verbose_name="course_status",
    )
    usercourseprogress = models.CharField(
        max_length=20,
        verbose_name="прогресс курса",
        choices=ProgressStatus.choices,
    )


class CourseFaq(models.Model):
    """Модель связи вопрос-курс."""

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        ordering = ("faq",)


class CourseKnowledge(models.Model):
    """Модель связи умение-курс."""

    knowledge = models.ForeignKey(Knowledge, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        ordering = ("knowledge",)


class Subscription(TimeStampedModel):
    """
    Модель для записи пользователя на курс.

    user - ForeignKey на модель user
    course - ForeignKey на модель course.
    enabled - признак активности записи на курс.
    """

    class Flag(models.TextChoices):
        ACTIVE = 1, "Запись активна"
        INACTIVE = 0, "Запись не активна"

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="student")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="course")
    enabled = models.CharField(
        max_length=20, choices=Flag.choices, verbose_name="статус записи на курс", default=Flag.ACTIVE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course",
            )
        ]
        ordering = ("user",)
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курс"

    def __str__(self):
        return f"<Subscription: {self.id}, user: {self.user_id}, course: {self.course_id}>"

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, F

from lizaalert.courses.mixins import TimeStampedModel, order_number_mixin
from lizaalert.quizzes.models import Quiz
from lizaalert.settings.base import CHAPTER_STEP, LESSON_STEP

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
    class CourseStatus(models.IntegerChoices):
        """Класс для выбора статуса курса."""

        DRAFT = 0, "в разработке"
        PUBLISHED = 1, "опубликован"
        ARCHIVE = 2, "в архиве"

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
    knowledge = models.ManyToManyField(
        Knowledge,
        through="CourseKnowledge",
        verbose_name="Умения",
    )
    faq = models.ManyToManyField(
        FAQ,
        through="CourseFaq",
        verbose_name="Часто задаваемые вопросы",
    )
    user_created = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Создатель курса")
    status = models.IntegerField(verbose_name="статус курса", choices=CourseStatus.choices, default=CourseStatus.DRAFT)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return f"Course {self.title}"

    def finish(self, user):
        """Закончить весь курс."""
        CourseProgressStatus.objects.get_or_create(
            user=user, course=self, usercourseprogress=CourseProgressStatus.ProgressStatus.FINISHED
        )

    def current_lesson(self, user):
        """Вернуть queryset текущего урока."""
        finished_lessons = LessonProgressStatus.objects.filter(
            user=user, userlessonprogress=LessonProgressStatus.ProgressStatus.FINISHED
        ).values_list("lesson", flat=True)

        return (
            Lesson.objects.filter(chapter__course=self, status=Lesson.LessonStatus.PUBLISHED)
            .exclude(id__in=finished_lessons)
            .annotate(ordering=F("chapter__order_number") + F("order_number"))
            .order_by("ordering")
        )


class Chapter(TimeStampedModel, order_number_mixin(CHAPTER_STEP, "course")):
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

    class Meta:
        ordering = ("order_number",)
        verbose_name = "глава"
        verbose_name_plural = "глава"

    def __str__(self):
        return f"Курс {self.course.title}: Глава {self.title}"

    def finish(self, user):
        """
        Закончить главу.

        В случае если, текущая глава является последним и остальные главы в курсе пройдены
        активируется метод finish() отмечающий прохождение курса этогй главы.
        """
        ChapterProgressStatus.objects.get_or_create(
            user=user, chapter=self, userchapterprogress=CourseProgressStatus.ProgressStatus.FINISHED
        )
        chapter_qs = Chapter.objects.filter(course=self.course).aggregate(total_chapters=Count("id"))
        progress_qs = ChapterProgressStatus.objects.filter(
            chapter__course=self.course, user=user, userchapterprogress=ChapterProgressStatus.ProgressStatus.FINISHED
        ).aggregate(finished_chapters=Count("id"))
        if chapter_qs["total_chapters"] == progress_qs["finished_chapters"]:
            self.course.finish(user)


class Lesson(TimeStampedModel, order_number_mixin(LESSON_STEP, "chapter")):
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

    class LessonStatus(models.IntegerChoices):
        DRAFT = 0, "В разработке"
        READY = 1, "Готов"
        PUBLISHED = 2, "Опубликован"

    title = models.CharField(max_length=120, verbose_name="название урока")
    chapter = models.ForeignKey(
        Chapter, on_delete=models.PROTECT, related_name="lessons", verbose_name="уроки главы", null=True
    )
    description = models.TextField(blank=True, null=True, verbose_name="описание урока")
    video_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на видеоурок")
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
    status = models.IntegerField(verbose_name="статус урока", choices=LessonStatus.choices, default=LessonStatus.DRAFT)
    additional = models.BooleanField(verbose_name="дополнительный урок", default=False)
    diploma = models.BooleanField(verbose_name="дипломный урок", default=False)

    class Meta:
        ordering = ("order_number",)
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f"Урок {self.id}: {self.title} (Глава {self.chapter_id})"

    def finish(self, user):
        """
        Закончить текущий урок.

        В случае если, текущий урок является последним и остальные уроки в главе пройдены
        активируется метод finish() отмечающий прохождение главы этого урока.
        """
        progress, created = LessonProgressStatus.objects.get_or_create(
            user=user, lesson=self, defaults={"userlessonprogress": LessonProgressStatus.ProgressStatus.FINISHED}
        )
        if not created:
            progress.userlessonprogress = LessonProgressStatus.ProgressStatus.FINISHED
            progress.save()
        lesson_qs = Lesson.objects.filter(chapter=self.chapter, status=self.LessonStatus.PUBLISHED).aggregate(
            total_lessons=Count("id")
        )
        progress_qs = LessonProgressStatus.objects.filter(
            lesson__chapter=self.chapter, user=user, userlessonprogress=LessonProgressStatus.ProgressStatus.FINISHED
        ).aggregate(finished_lessons=Count("id"))
        if lesson_qs["total_lessons"] == progress_qs["finished_lessons"]:
            self.chapter.finish(user)

    @property
    def ordered(self):
        """Вернуть очередность всех уроков курса с полем ordering."""
        return (
            Lesson.objects.filter(chapter__course=self.chapter.course)
            .annotate(ordering=F("chapter__order_number") + F("order_number"))
            .order_by("ordering")
        )

    @property
    def next_lesson(self):
        """Вернуть следующий по очереди урок."""
        ordered_lessons = self.ordered
        return ordered_lessons.filter(ordering__gt=self.ordering).order_by("ordering")[:1]

    @property
    def prev_lesson(self):
        """Вернуть предыдущий по очереди урок."""
        ordered_lessons = self.ordered
        return ordered_lessons.filter(ordering__lt=self.ordering).order_by("-ordering")[:1]


class LessonProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении уроков в главе и курсе. Наследуется от TimeStampedModel.

    Поля модели:

    lesson - тип ForeignKey к модели  Lesson
    user - тип ForeignKey к модели User
    usercourseprogress - статус прохождения урока
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
        default=0,
    )
    version_number = models.PositiveSmallIntegerField(
        "Номер версии урока", validators=[MinValueValidator(1)], default=1
    )

    def __str__(self):
        return f"Lesson {self.lesson_id}: {self.user_id} Progress: {self.get_userlessonprogress_display()}"

    class Meta:
        verbose_name = "Прогресс по уроку"
        verbose_name_plural = "Прогресс по урокам"
        ordering = ("user",)


class ChapterProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении главы. Наследуется от TimeStampedModel.

    Поля модели:

    глава - тип ForeignKey к модели Chapter
    user - тип ForeignKey к модели User
    userchapterprogress - статус прохождения главы
    """

    class ProgressStatus(models.TextChoices):
        """класс по определению статуса прохождения урока, главы, курса, возможно тестов."""

        NOTSTARTED = 0, "Не начата"
        INPROGRESS = 1, "Начата"
        FINISHED = 2, "Пройдена"

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

    def __str__(self):
        return f"Chapter {self.chapter.title}: {self.user.username}"

    class Meta:
        verbose_name = "Прогресс по главе"
        verbose_name_plural = "Прогресс по главам"
        ordering = ("user",)


class CourseProgressStatus(TimeStampedModel):
    """
    Класс для хранения прогресса студента при прохождении курса. Наследуется от TimeStampedModel.

    Поля модели:

    курс - тип ForeignKey к модели Course
    user - тип ForeignKey к модели User
    usercourseprogress - статус прохождения курса
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

    def __str__(self):
        return f"Course {self.course.title}: {self.user.username}"

    class Meta:
        verbose_name = "Прогресс по курсу"
        verbose_name_plural = "Прогресс по курсам"
        ordering = ("user",)


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

from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import DateField, F, Max, Q, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from lizaalert.courses.exceptions import AlreadyExistsException, NoSuitableCohort, ProgressNotFinishedException
from lizaalert.courses.mixins import TimeStampedModel, order_number_mixin, status_update_mixin
from lizaalert.courses.signals import course_finished
from lizaalert.courses.utils import check_finished_content
from lizaalert.quizzes.models import Quiz
from lizaalert.settings.constants import CHAPTER_STEP, LESSON_STEP

User = get_user_model()


class BaseProgress(models.Model):
    """Progress mixin."""

    class ProgressStatus(models.IntegerChoices):
        """Класс по определению статуса прохождения урока, главы, курса."""

        NOT_STARTED = 0, "Не начат"
        ACTIVE = 1, "Начат"
        FINISHED = 2, "Пройден"

    progress = models.IntegerField(
        verbose_name="прогресс",
        choices=ProgressStatus.choices,
        default=0,
    )

    class Meta:
        abstract = True


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


class Course(
    TimeStampedModel,
    status_update_mixin(),
):
    class CourseStatus(models.IntegerChoices):
        """Класс для выбора статуса курса."""

        DRAFT = 0, "в разработке"
        PUBLISHED = 1, "опубликован"
        ARCHIVE = 2, "в архиве"

    title = models.CharField(max_length=120, verbose_name="Название курса")
    course_format = models.CharField(max_length=60, verbose_name="Формат курса")
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

    def current_lesson(self, user):
        """Return queryset of the current lesson."""
        finished_lessons = LessonProgressStatus.objects.filter(
            subscription__user=user, progress=LessonProgressStatus.ProgressStatus.FINISHED
        ).values_list("lesson_id", flat=True)

        lesson_queryset = Lesson.objects.filter(chapter__course=self, status=Lesson.LessonStatus.PUBLISHED).annotate(
            ordering=F("chapter__order_number") + F("order_number")
        )
        current_lesson_queryset = lesson_queryset.exclude(id__in=finished_lessons).order_by("ordering")[:1]

        if not current_lesson_queryset.exists():
            return lesson_queryset.order_by("-ordering")[:1]

        return current_lesson_queryset

    def subscribe(self, user):
        """Подписать пользователя на данный курс."""
        subscription, created = Subscription.objects.get_or_create(user=user, course=self)
        if not created:
            raise AlreadyExistsException({"detail": "Already enrolled."})
        return subscription

    def finish(self, subscription):
        """Завершить данный курс."""
        uncompleted_lessons = (
            Lesson.objects.filter(
                chapter__course=self,
                status=Lesson.LessonStatus.PUBLISHED,
            )
            .exclude(
                id__in=LessonProgressStatus.objects.filter(
                    subscription=subscription, progress=LessonProgressStatus.ProgressStatus.FINISHED
                ).values_list("lesson_id", flat=True)
            )
            .exists()
        )
        if uncompleted_lessons:
            raise ProgressNotFinishedException()
        super().finish(subscription)
        subscription.finish()

    def activate(self, subscription):
        super().activate(subscription)
        user = subscription.user
        progress_status, created = Subscription.objects.get_or_create(
            user=user, course=self, defaults={"status": Subscription.Status.IN_PROGRESS}
        )
        if not created:
            progress_status.status = Subscription.Status.IN_PROGRESS
            progress_status.save()

    def get_achievements(self, course, user):
        """
        Отправляет сигнал о завершении курса для получения ачивок.

        Передает course_id и user.
        """
        course_finished.send(sender=self.__class__, course=course, user=user)


class Chapter(TimeStampedModel, order_number_mixin(CHAPTER_STEP, "course"), status_update_mixin(parent="course")):
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


class Lesson(
    TimeStampedModel,
    order_number_mixin(LESSON_STEP, "chapter"),
    status_update_mixin(parent="chapter", publish_status="LessonStatus"),
):
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
        HOMEWORK = "Homework", "Домашнее задание"

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

    def finish(self, subscription):
        """Завершить данный урок."""
        if not check_finished_content(self, subscription, lesson_type=[Lesson.LessonType.HOMEWORK]):
            raise ProgressNotFinishedException("Необходимый контент урока не пройден.")
        super().finish(subscription)


class LessonProgressStatus(TimeStampedModel, BaseProgress):
    """
    Класс для хранения прогресса студента при прохождении уроков в главе и курсе. Наследуется от TimeStampedModel.

    Поля модели:

    lesson - тип ForeignKey к модели  Lesson
    user - тип ForeignKey к модели User
    progress - статус прохождения урока
    version_number - номер версии урока(предусматриваем для будующего использования, значение по умолчанию 1)
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="lesson_progress")
    version_number = models.PositiveSmallIntegerField(
        "Номер версии урока", validators=[MinValueValidator(1)], default=1
    )
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        verbose_name="Подписка",
        related_name="lesson_progress",
    )

    def __str__(self):
        return f"Lesson {self.lesson_id}: {self.subscription_id} Progress: {self.get_progress_display()}"

    class Meta:
        verbose_name = "Прогресс по уроку"
        verbose_name_plural = "Прогресс по урокам"
        ordering = ("subscription",)


class ChapterProgressStatus(TimeStampedModel, BaseProgress):
    """
    Класс для хранения прогресса студента при прохождении главы. Наследуется от TimeStampedModel.

    Поля модели:

    глава - тип ForeignKey к модели Chapter
    user - тип ForeignKey к модели User
    progress - статус прохождения главы
    """

    chapter = models.ForeignKey(Chapter, on_delete=models.PROTECT, related_name="chapter_progress")
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        verbose_name="Подписка",
        related_name="chapter_progress",
    )

    def __str__(self):
        return f"Chapter {self.chapter.title}: {self.subscription_id}"

    class Meta:
        verbose_name = "Прогресс по главе"
        verbose_name_plural = "Прогресс по главам"
        ordering = ("subscription",)


class CourseProgressStatus(TimeStampedModel, BaseProgress):
    """
    Класс для хранения прогресса студента при прохождении курса. Наследуется от TimeStampedModel.

    Поля модели:

    курс - тип ForeignKey к модели Course
    user - тип ForeignKey к модели User
    progress - статус прохождения курса
    """

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="course_progress")
    subscription = models.ForeignKey(
        "Subscription",
        on_delete=models.CASCADE,
        verbose_name="Подписка",
        related_name="course_progress",
    )

    def __str__(self):
        return f"Course {self.course.title}: {self.subscription_id}"

    class Meta:
        verbose_name = "Прогресс по курсу"
        verbose_name_plural = "Прогресс по курсам"
        ordering = ("subscription",)


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


class Cohort(TimeStampedModel):
    """
    Модель для представления группы курса.

    Поля модели:
    - course: ForeignKey к модели Course
    - cohort_number: уникальный номер группы в рамках курса
    - start_date: дата начала обучения
    - end_date: дата окончания обучения
    - students_count: количество студентов в группе
    - teacher: имя преподавателя группы
    """

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="cohorts", verbose_name="Курс")
    cohort_number = models.PositiveIntegerField(
        verbose_name="Номер группы", blank=True, help_text="Данное поле будет рассчитано автоматически при сохранении."
    )
    start_date = models.DateField(
        verbose_name="Дата начала",
        null=True,
        blank=True,
        help_text="Не заполняйте это поле, если хотите, чтобы группа была доступна всегда.",
    )
    end_date = models.DateField(
        verbose_name="Дата окончания",
        null=True,
        blank=True,
        help_text="Не заполняйте это поле, если хотите, чтобы группа была доступна всегда.",
    )
    students_count = models.PositiveIntegerField(
        verbose_name="Текущее количество студентов", null=True, blank=True, default=0
    )
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Преподаватель")
    max_students = models.PositiveIntegerField(
        verbose_name="Максимальное количество студентов",
        null=True,
        blank=True,
        default=None,
        help_text="Не заполняйте это поле, если хотите, чтобы группа была доступна всегда.",
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["course", "cohort_number"],
                name="unique_course_cohort_number",
            )
        ]
        verbose_name = "Когорта"
        verbose_name_plural = "Когорты"
        ordering = ("start_date",)

    def save(self, *args, **kwargs):
        if not self.pk:
            max_cohort_number = Cohort.objects.filter(course=self.course).aggregate(Max("cohort_number"))[
                "cohort_number__max"
            ]

            self.cohort_number = max_cohort_number + 1 if max_cohort_number is not None else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Курс {self.course_id} - Когорта {self.cohort_number}"

    @property
    def is_available(self):
        """
        Проверить доступность курса.

        Если дата начала курса не указана, то курс доступен всегда.
        """
        if self.start_date:
            return timezone.now().date() >= self.start_date
        return True


class Subscription(TimeStampedModel):
    """
    Модель для записи пользователя на курс.

    user - ForeignKey на модель user
    course - ForeignKey на модель course.
    status - признак активности записи на курс.
    """

    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Записан на курс"
        NOT_ENROLLED = "not_enrolled", "Запись не активна"
        IN_PROGRESS = "in_progress", "Курс проходится"
        AVAILABLE = "available", "Курс доступен"
        COMPLETED = "completed", "Курс пройден"

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="subscriptions")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="+")
    status = models.CharField(
        max_length=20, choices=Status.choices, verbose_name="статус записи на курс", default=Status.ENROLLED
    )

    cohort = models.ForeignKey(
        Cohort, on_delete=models.PROTECT, related_name="subscriptions", null=True, blank=True, verbose_name="Группа"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course",
            ),
        ]

        ordering = ("user",)
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курс"

    def __str__(self):
        return f"<Subscription: {self.id}, user: {self.user_id}, course: {self.course_id}>"

    def save(self, *args, **kwargs):
        """
        Найти подходящую когорту для записи на курс.

        Ищем когорту с датой начала, которая меньше или равна текущей дате и в которой есть места.
        Если не найдена, ищем универсальную когорту без даты начала и без максимального количества студентов.
        Увеличиваем количество студентов в когорте на 1.
        В случае отсутствия подходящей когорты, вызываем исключение NoSuitableCohort.
        Во время исполнения функции поддерживается атомарность транзакции и блокируется найденная когорта.
        """
        if not self.pk:
            with transaction.atomic():
                current_date = timezone.now().date()
                # Создается дата в далеком будущем для корректной сортировки ближайших когорт
                far_future_date = datetime(9999, 1, 1).date()
                cohort = (
                    Cohort.objects.select_for_update()
                    .annotate(
                        sorted_start_date=Coalesce("start_date", Value(far_future_date, output_field=DateField()))
                    )
                    .filter(
                        Q(start_date__gte=current_date, students_count__lt=F("max_students"))
                        | Q(start_date=None, max_students=None),
                        course=self.course,
                    )
                    .order_by("sorted_start_date")
                    .first()
                )

                if cohort:
                    Cohort.objects.filter(pk=cohort.pk).update(students_count=F("students_count") + 1)
                    self.cohort = cohort
                else:
                    raise NoSuitableCohort()
        super().save(*args, **kwargs)

    def finish(self):
        """Завершить подписку на курс."""
        self.status = Subscription.Status.COMPLETED
        self.save()

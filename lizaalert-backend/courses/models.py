from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=120, verbose_name="Название курса")
    format = models.CharField(max_length=60, verbose_name="Формат курса")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала курса")
    cover_path = models.FileField(blank=True, null=True, verbose_name="Путь к обложке курса")
    short_description = models.CharField(max_length=120, verbose_name="Краткое описание курса")
    level = models.ForeignKey("users.Level", on_delete=models.PROTECT, verbose_name="Уровень", related_name='course')
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
    name = models.CharField("Статус курса", max_length=50, editable=False)
    slug = models.SlugField(max_length=20, editable=False)

    class Meta:
        db_table = "course_status"
        verbose_name = "Статус курса"
        verbose_name_plural = "Статус курсов"

    def __str__(self):
        return f"{self.slug}"


class Lesson(models.Model):
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
    ready* - статус готовности готов/не готов
    visible* - статус видимости урока вкл./выкл
    published* - статус публикации урока, опубликован - да/нет
    additional* - дополнительный урок - да/нет
    diploma* - дипломный урок - да/нет
    created_at* - дата создания записи об уроке, автоматическое проставление текущего времени
    updated_at* - дата обновления записи об уроке, автоматическое проставление текущего времени.
    """

    LESSON = "Lesson"
    VIDEOLESSON = "Videolesson"
    WEBINAR = "Webinar"
    QUIZZE = "Quizze"
    TYPE_CHOICES = ((LESSON, "Урок"), (VIDEOLESSON, "Видеоурок"), (WEBINAR, "Вебинар"), (QUIZZE, "Тест"))

    title = models.CharField(max_length=120, verbose_name="название урока")
    description = models.TextField(blank=True, null=True, verbose_name="описание урока")
    lesson_type = models.CharField(blank=True, null=True, max_length=20, verbose_name="тип урока",
                                   choices=TYPE_CHOICES)
    tags = models.CharField(max_length=255, verbose_name="ключевые слова урока")
    duration = models.PositiveSmallIntegerField(verbose_name="продолжительность урока")
    user_created = models.ForeignKey(User, related_name="lesson_creator", on_delete=models.PROTECT,
                                     verbose_name="пользователь, создавший урок")
    user_modifier = models.ForeignKey(User, related_name="lesson_editor", on_delete=models.PROTECT,
                                      verbose_name="пользователь, внёсший изменения в урок")
    ready = models.BooleanField(verbose_name="статус готовности", default=False)
    visible = models.BooleanField(verbose_name="статус видимости урока", default=True)
    published = models.BooleanField(verbose_name="статус публикации урока", default=False)
    additional = models.BooleanField(verbose_name="дополнительный урок", default=False)
    diploma = models.BooleanField(verbose_name="дипломный урок", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания урока")
    update_at = models.DateTimeField(auto_now=True, verbose_name="дата изменения урока")

    class Meta:
        ordering = ('title',)
        verbose_name = "урок"
        verbose_name_plural = "урок"

    def __str__(self):
        return self.title


class Chapter(models.Model):
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
    lessons = models.ManyToManyField(Lesson, through='ChapterLesson', verbose_name="Уроки главы")
    user_created = models.ForeignKey(User, related_name="chapter_creator", on_delete=models.PROTECT,
                                     verbose_name="пользователь, создавший главу")
    user_modifier = models.ForeignKey(User, related_name="chapter_editor", on_delete=models.PROTECT,
                                      verbose_name="пользователь, внёсший изменения в главу")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания главы")
    update_at = models.DateTimeField(auto_now=True, verbose_name="дата изменения главы")

    class Meta:
        ordering = ('title',)
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
    order_number = models.PositiveSmallIntegerField("порядковый номер урока в главе", unique=True,
                                                    validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата добавления урока в главу")

    class Meta:
        ordering = ('order_number',)
        unique_together = ['chapter', 'lesson']


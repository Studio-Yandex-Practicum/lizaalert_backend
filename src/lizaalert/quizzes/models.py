from django.contrib.auth import get_user_model
from django.db import models

from lizaalert.quizzes.managers import QuestionManager
from .mixins import TimeStampedMixin

User = get_user_model()


class Quiz(TimeStampedMixin):
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Автор",
    )
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Вопрос")
    duration_minutes = models.PositiveIntegerField("Кол-во минут для сдачи", default=0)
    passing_score = models.PositiveIntegerField("Кол-во баллов для прохождения", default=0)
    retries = models.PositiveIntegerField("Число попыток", default=0)
    slug = models.SlugField(unique=True)
    status = models.CharField("Статус", max_length=20)
    in_progress = models.BooleanField("В процессе", default=False)
    deadline = models.DateTimeField("Срок выполнения")

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"

    def __str__(self):
        return self.title


class Question(TimeStampedMixin):
    QUESTION_TYPES = [
        ("checkbox", "checkbox"),
        ("radio", "radio"),
        ("text_answer", "Text Answer"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, verbose_name="Квиз")
    question_type = models.CharField("Тип вопроса", max_length=20, choices=QUESTION_TYPES)
    title = models.CharField("Заголовок", max_length=255)
    answers = models.JSONField("[id, title, description, right_answer:bool]")
    order_number = models.PositiveIntegerField("Порядковый номер")
    objects = QuestionManager()

    class Meta:
        ordering = ["order_number"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class UserAnswer(TimeStampedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answers = models.JSONField("Ответы пользователя")
    result = models.JSONField("Результат проверки ответов")
    retry_count = models.PositiveIntegerField("Количество попыток", default=0)
    score = models.PositiveIntegerField("Количество баллов", default=0)
    final_result = models.CharField("Окончательный результат", max_length=255)
    start_time = models.TimeField("Время начала выполнения", null=True, blank=True)
    date_completed = models.TimeField("Время завершения выполнения", null=True, blank=True)

    class Meta:
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"

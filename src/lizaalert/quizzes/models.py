from django.contrib.auth import get_user_model
from django.db import models

from lizaalert.courses.mixins import TimeStampedModel
from lizaalert.quizzes.managers import QuestionManager

User = get_user_model()


class Quiz(TimeStampedModel):
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
    status = models.CharField("Статус", max_length=20)
    in_progress = models.BooleanField("В процессе", default=False)
    deadline = models.DateTimeField("Срок выполнения")

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    QUESTION_TYPES = [
        ("checkbox", "checkbox"),
        ("radio", "radio"),
        ("text_answer", "Text Answer"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, verbose_name="Квиз", related_name="questions")
    question_type = models.CharField("Тип вопроса", max_length=20, choices=QUESTION_TYPES)
    title = models.CharField("Заголовок", max_length=255)
    content = models.JSONField("Варианты ответов", default=list, blank=True)
    order_number = models.PositiveIntegerField("Порядковый номер")
    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class UserAnswer(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answers = models.JSONField("Ответы пользователя", null=True, blank=True)
    result = models.JSONField("Результат проверки ответов", null=True, blank=True)
    retry_count = models.PositiveIntegerField("Количество попыток", default=0)
    score = models.PositiveIntegerField("Количество баллов", default=0)
    final_result = models.CharField("Окончательный результат", max_length=255, null=True, blank=True)
    start_date = models.DateTimeField("Время начала выполнения", null=True, blank=True)
    end_date = models.DateTimeField("Время завершения выполнения", null=True, blank=True)

    class Meta:
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"

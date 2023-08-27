from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Quiz(models.Model):
    author = models.ForeignKey(
        User,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Автор",
    )
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Вопрос")
    duration_minutes = models.PositiveIntegerField("Кол-во минут для сдачи", default=0)
    passing_score = models.PositiveIntegerField("Кол-во баллов для прохождения", default=0)
    max_attempts = models.PositiveIntegerField("Число попыток", default=1)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    deleted_at = models.DateTimeField("Дата удаления", null=True, blank=True)

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"


class Question(models.Model):
    QUESTION_TYPES = [
        ("single_choice", "Single Choice"),
        ("multiple_choice", "Multiple Choice"),
        ("text_answer", "Text Answer"),
    ]

    question_type = models.CharField("Тип вопроса", max_length=20, choices=QUESTION_TYPES)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, verbose_name="Квиз")
    title = models.CharField("Заголовок", max_length=255)
    answers = models.JSONField("[id, title, description, right_answer:bool]")
    order_number = models.PositiveIntegerField("Порядковый номер")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    deleted_at = models.DateTimeField("Дата удаления", null=True, blank=True)

    class Meta:
        ordering = ["-order_number"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class UserAnswer(models.Model):
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

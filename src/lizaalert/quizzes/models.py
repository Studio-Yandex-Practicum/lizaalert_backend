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


class Question(models.Model):
    QUESTION_TYPES = [
        ("single_choice", "Single Choice"),
        ("multiple_choice", "Multiple Choice"),
        ("text_answer", "Text Answer"),
    ]

    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    answers = models.JSONField()
    order_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-order_number"]

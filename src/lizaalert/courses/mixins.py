from django.db import models, transaction


class TimeStampedModel(models.Model):
    """
    Абстрактная модель времени создания или изменения данных.

    created_at* - дата создания записи об уроке, автоматическое проставление
    текущего времени
    updated_at* - дата обновления записи об уроке, автоматическое проставление
    текущего времени.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ActivateLessonMixin(models.Model):
    """Абстрактная модель активации прохождения урока."""

    class Meta:
        abstract = True

    @transaction.atomic
    def activate(self, user):
        """Проверить отсутствие активных уроков, затем активировать урок."""
        from lizaalert.courses.models import Lesson, LessonProgressStatus

        check_lessons = Lesson.objects.filter(
            chapter__course=self.chapter.course,
            lesson_progress__userlessonprogress=LessonProgressStatus.ProgressStatus.ACTIVE,
            lesson_progress__user=user,
        ).count()
        if check_lessons > 0:
            raise ValueError("You can't have more than one active lesson.")

        LessonProgressStatus.objects.get_or_create(
            user=user, lesson=self, userlessonprogress=LessonProgressStatus.ProgressStatus.ACTIVE
        )

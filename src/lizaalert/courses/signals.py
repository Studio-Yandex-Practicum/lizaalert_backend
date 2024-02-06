from django.core.exceptions import ValidationError
from django.dispatch import Signal, receiver

from lizaalert.users.utils import (
    assign_achievements_for_completion,
    assign_achievements_for_course,
    increment_completed_courses_count,
)

# Сигнал отправляется при завершении курса
course_finished = Signal(providing_args=["course", "user"])


@receiver(course_finished)
def handle_course_finished(sender, **kwargs):
    """
    Обработчик сигнала завершения курса.

    При получении сигнала выполняет инкремент счетчика завершенных курсов пользователя
    и присваивает соответствующие достижения.
    """
    course = kwargs.get("course")
    user = kwargs.get("user")

    if not course or not user:
        raise ValidationError("Invalid signal data: course and user are required.")

    course_id = course.id

    increment_completed_courses_count(user)
    assign_achievements_for_course(user, course_id)
    assign_achievements_for_completion(user, course_id)

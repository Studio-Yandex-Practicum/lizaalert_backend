from django.dispatch import Signal, receiver

from lizaalert.users.utils import assign_achievements, increment_completed_courses_count

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
    course_id = course.id
    user = kwargs.get("user")

    increment_completed_courses_count(user)
    assign_achievements(user, course_id)

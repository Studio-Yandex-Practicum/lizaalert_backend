from django.dispatch import Signal

# Сигнал отправляется при завершении курса
course_finished = Signal(providing_args=["course_id", "user"])

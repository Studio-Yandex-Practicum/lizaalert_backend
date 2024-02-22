from rest_framework.exceptions import NotFound


class NoSuitableWebinar(NotFound):
    """Не нашлось подходящего вебинара."""

    default_detail = "Подходящий вебинар не найден."

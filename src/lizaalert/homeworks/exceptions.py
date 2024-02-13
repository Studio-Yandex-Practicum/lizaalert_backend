from rest_framework import status
from rest_framework.exceptions import APIException


class HomeworkException(APIException):
    """Базовый класс для исключений, связанных с квизами."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Некорректный запрос"

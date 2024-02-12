from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


class BadRequestException(ValidationError):
    pass


class AlreadyExistsException(PermissionDenied):
    pass


class SubscriptionDoesNotExist(PermissionDenied):
    """Исключение для подписки для данного пользователя на данный курс."""

    default_detail = "Subscription does not exist"


class NoSuitableCohort(NotFound):
    """Исключение для подписки для данного пользователя на данный курс."""

    default_detail = "Не получилось найти подходящую когорту для данного курса"


class ProgressNotFinishedException(PermissionDenied):
    """Исключение для завершения курса при незавершенных уроках."""

    default_detail = "Имеются незавершенные уроки"

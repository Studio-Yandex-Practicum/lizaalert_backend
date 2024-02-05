from rest_framework.exceptions import PermissionDenied, ValidationError


class BadRequestException(ValidationError):
    pass


class AlreadyExistsException(PermissionDenied):
    pass


class SubscriptionDoesNotExist(PermissionDenied):
    """Исключение для подписки для данного пользователя на данный курс."""

    default_detail = "Subscription does not exist"


class ProgressNotFinishedException(PermissionDenied):
    """Исключение для завершения курса при незавершенных уроках."""

    default_detail = "Имеются незавершенные уроки"

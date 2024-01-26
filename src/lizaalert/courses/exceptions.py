from rest_framework.exceptions import PermissionDenied, ValidationError


class BadRequestException(ValidationError):
    pass


class AlreadyExistsException(PermissionDenied):
    pass


class SubscriptionDoesNotExist(PermissionDenied):

    def __init__(self, detail=None):
        if detail is None:
            detail = "You do not have a subscription to this course."
        super().__init__(detail=detail)

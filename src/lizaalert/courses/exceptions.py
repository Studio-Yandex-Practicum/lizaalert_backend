from rest_framework.exceptions import PermissionDenied, ValidationError


class BadRequestException(ValidationError):
    pass


class AlreadyExistsException(PermissionDenied):
    pass

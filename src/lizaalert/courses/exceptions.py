from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request."
    default_code = "bad_request"


class AlreadyExistsException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Forbidden."
    default_code = "forbidden"

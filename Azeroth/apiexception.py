from rest_framework.exceptions import APIException
from rest_framework import status

class NotLogin(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = '请登陆.....'
    default_code = 'not_authenticated'
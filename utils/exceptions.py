from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from backend.settings import DEBUG

def handler(e, ctx):
    resp = exception_handler(e, ctx)

    if resp is not None:
        if type(e) is exceptions.Throttled:
            resp.data['code'] = -3
        elif type(e) is exceptions.PermissionDenied:
            resp.data['code'] = -2
        elif type(e) is exceptions.AuthenticationFailed:
            resp.data['code'] = -4
        elif type(e) is ParamErr:
            resp.data['code'] = -1
        elif type(e) is Failure:
            resp.data['code'] = 1
        else:
            resp.data['code'] = -100

    return resp

class Failure(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Fail.'

class ParamErr(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Invalid parameters.'

    def __init__(self, info=''):
        if DEBUG and len(info):
            self.detail += ' ' + info


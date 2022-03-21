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
            resp.data['code'] = -1
        else:
            resp.data['code'] = -4

    return resp

class ParamErr(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Invalid parameters.'

    def __init__(self, info=''):
        if DEBUG and len(info):
            self.detail += ' ' + info


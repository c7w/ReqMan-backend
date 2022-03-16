from django.http import JsonResponse
from rest_framework.views import exception_handler

def handler(e, ctx):
    resp = exception_handler(e, ctx)

    if resp is not None:
        resp.data['code'] = -1

    return resp

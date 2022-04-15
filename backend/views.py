from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view


@api_view(["POST"])
def root(req):
    resp = {}
    for k, v in req.META.items():
        if type(v) == str:
            resp[k] = v
    header = resp
    body = req.data

    return JsonResponse({"header": header, "body": body})

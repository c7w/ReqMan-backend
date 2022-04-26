from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from ums.models import Config
import json
from utils.model_date import get_timestamp


@api_view(["POST"])
def root(req):
    # resp = {}
    # for k, v in req.META.items():
    #     if type(v) == str:
    #         resp[k] = v
    # header = resp
    # body = req.data
    #
    # Config.objects.create(
    #     key=str(get_timestamp()),
    #     value=json.dumps({"header": header, "body": body}, ensure_ascii=False),
    # )
    #
    # return JsonResponse({"header": header, "body": body})
    return JsonResponse({"message": "c7w, yyds!"})

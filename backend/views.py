from django.http import JsonResponse, HttpRequest
from rest_framework.decorators import api_view
from ums.models import Config
import json
from utils.model_date import get_timestamp


@api_view(["POST"])
def root(req):
    return JsonResponse({"message": "c7w, yyds!"})

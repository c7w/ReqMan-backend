from django.http import JsonResponse


def root(req):
    print(123)
    return JsonResponse({"status": "ok"})

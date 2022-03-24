from django.http import JsonResponse


def root(req):
    return JsonResponse({"status": "ok", "META": (req.META.get('HTTP_X_FORWARDED_FOR'), req.META['REMOTE_ADDR'])})

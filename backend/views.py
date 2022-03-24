from django.http import JsonResponse


def root(req):
    resp = {}
    for k, v in req.META.items():
        if type(v) == str:
            resp[k] = v
    print(resp)
    return JsonResponse(resp)

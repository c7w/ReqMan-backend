from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from utils.exceptions import ParamErr
from ums.models import User
from utils.sessions import SessionAuthentication

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    @action(detail=False)
    def check_username_available(self, req: Request):
        name = req.GET.get('name')
        if not name:
            raise ParamErr('lacking name in GET')
        usr = User.objects.filter(name=name).first()
        return Response({
            'code': 1 if usr else 0
        })

    @action(detail=False)
    def check_email_available(self, req: Request):
        email = req.GET.get('email')
        if not email:
            raise ParamErr('lacking email in GET')
        usr = User.objects.filter(email=email).first()
        return Response({
            'code': 1 if usr else 0
        })



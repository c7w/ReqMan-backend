from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from utils.exceptions import ParamErr
from ums.models import User
from utils.sessions import SessionAuthentication
from argon2 import PasswordHasher
from ums.utils import *

def require(lst, attr_name):
    attr = lst.get(attr_name)
    if not attr:
        raise ParamErr(f'missing {attr_name}.')
    return attr

SUCC = Response({
    'code': 0
})

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    @action(detail=False)
    def check_username_available(self, req: Request):
        name = require(req.GET, 'name')
        return Response({
            'code': 1 if name_dup(name) else 0
        })

    @action(detail=False)
    def check_email_available(self, req: Request):
        email = require(req.GET, 'email')
        return Response({
            'code': 1 if email_dup(email) else 0
        })

    @action(detail=False, methods=['POST'])
    def register(self, req: Request):
        name = require(req.POST, 'name')
        password = require(req.POST, 'password')
        email = require(req.POST, 'email')
        invitation = req.POST.get('invitation')

        if name_dup(name):
            return Response({
                'code': 1,
                'field': 'name dup'
            })

        if not email_valid(email):
            return Response({
                'code': 2,
                'field': 'email invalid'
            })

        if email_dup(email):
            return Response({
                'code': 3,
                'field': 'email dup'
            })

        ph = PasswordHasher()
        password = ph.hash(password)

        User.objects.create(name=name, password=password, email=email)

        return SUCC







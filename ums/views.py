from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from utils.exceptions import ParamErr
from ums.models import User
from utils.sessions import *
# from argon2 import PasswordHasher
from ums.utils import *
from django.forms.models import model_to_dict

def require(lst, attr_name):
    """
    Require a field in parameter lst.
    If it does not exist, raise ParamErr
    """
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
            'code': 1 if name_exist(name) else 0
        })

    @action(detail=False)
    def check_email_available(self, req: Request):
        email = require(req.GET, 'email')
        return Response({
            'code': 1 if email_exist(email) else 0
        })

    @action(detail=False, methods=['POST'])
    def register(self, req: Request):
        name = require(req.POST, 'name')
        password = require(req.POST, 'password')
        email = require(req.POST, 'email')
        invitation = req.POST.get('invitation')

        if name_valid(name) \
            and not name_exist(name) \
            and email_valid(email) \
            and not email_exist(email):
            User.objects.create(name=name, password=password, email=email)
            return SUCC

        return Response({
            'code': 1
        })

    @action(detail=False, methods=['POST'])
    def login(self, req: Request):
        if req.user:
            return Response({
                'code': 1
            })

        identity = require(req.POST, 'identity')
        password = require(req.POST, 'password')

        if name_valid(identity):
            usr = name_exist(identity)
            if usr:
                if usr.password == password:
                    bind_session_id(req.COOKIES['sessionId'], usr)
                    return SUCC
                else:
                    return Response({
                        'code': 3
                    })
            else:
                return Response({
                    'code': 2
                })
        elif email_valid(identity):
            usr = email_exist(identity)
            if usr:
                if usr.password == password:
                    bind_session_id(req.COOKIES['sessionId'], usr)
                    return SUCC
                else:
                    return Response({
                        'code': 3
                    })
            else:
                return Response({
                    'code': 2
                })
        else:
            return Response({
                'code': 2
            })

    @action(detail=False, methods=['POST'])
    def logout(self, req: Request):
        if not req.user:
            return Response({
                'code': 1
            })

        disable_session_id(req.auth)
        return Response({
            'code': 0
        })

    @action(detail=False)
    def user(self, req: Request):
        if not req.user:
            return Response({
                'code': 1
            })
        return Response({
            'user': model_to_dict(req.user, exclude=[
                'password',
                'disabled'
            ]),
            'projects': [],
            'schedule':{
                'done': [],
            }
        })



from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from utils.exceptions import ParamErr
from ums.models import *
from utils.sessions import *
from ums.utils import *
from django.forms.models import model_to_dict

DEFAULT_INVITED_ROLE = 'member'

def require(lst, attr_name):
    """
    Require a field in parameter lst.
    If it does not exist, raise ParamErr
    """
    attr = lst.get(attr_name)
    if not attr:
        raise ParamErr(f'missing {attr_name}.')
    return attr

def intify(inp):
    if type(inp) == int:
        return inp

    try:
        return int(inp)
    except ValueError:
        raise ParamErr(f"{inp} cannot be convert to an integer")

def user_to_list(user: User):
    return model_to_dict(user, exclude=[
        'password',
        'disabled',
        'project'
    ])

def proj_to_list(proj: Project):
    return model_to_dict(proj, exclude=[
        'disabled'
    ])

SUCC = Response({
    'code': 0
})
FAIL = Response({
                'code': 1
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
        name = require(req.data, 'name')
        password = require(req.data, 'password')
        email = require(req.data, 'email')
        invitation = req.data.get('invitation')
        relation = None
        if invitation:
            relation = ProjectInvitationAssociation.\
                objects.filter(invitation=invitation).first()
            if not relation:
                return Response({
                    'code': 2
                })

        if name_valid(name) \
            and not name_exist(name) \
            and email_valid(email) \
            and not email_exist(email):
            usr = User.objects.create(name=name, password=password, email=email)
            if relation:
                UserProjectAssociation.objects.create(
                    project=relation.project,
                    user=usr,
                    role=relation.role
                )
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

        identity = require(req.data, 'identity')
        password = require(req.data, 'password')

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
            return FAIL
        return Response({
            'code': 0,
            'data': {
                'user': user_to_list(req.user),
                'projects': [model_to_dict(p, exclude=['disabled'])
                             for p in req.user.project.all()],
                'schedule': {
                    'done': [],
                    'wip': [],
                    'todo': []
                }
            }
        })

    @action(detail=False, methods=['POST'])
    def modify_user_role(self, req:Request):
        proj = intify(require(req.data, 'project'))
        user = intify(require(req.data, 'user'))
        role = require(req.data, 'role')

        # params check
        if role not in Role:
            return FAIL

        user = user_exist(user)
        if not user:
            return FAIL

        proj = proj_exist(proj)
        if not proj:
            return FAIL

        # supermaster check
        if not is_role(req.user, proj, 'supermaster'):
            return FAIL

        relation = UserProjectAssociation(user=user, proj=proj)
        if not relation:
            return FAIL
        relation.role = role
        relation.save()

        return SUCC

    @action(detail=False, methods=['POST'])
    def project(self,  req: Request):
        proj = intify(require(req.data, 'project'))

        proj = proj_exist(proj)
        if not proj:
            return FAIL

        if not in_proj(req.user, proj):
            return FAIL

        users = [user_to_list(u) for u in all_users().filter(project=proj)]
        proj = proj_to_list(proj)

        return Response({
            'code': 0,
            'data': {
                'project': proj,
                'users': users
            }
        })



    @action(detail=False, methods=['POST'])
    def modify_project(self, req: Request):
        pass

    @action(detail=False, methods=['POST'])
    def refresh_invitation(self, req: Request):
        proj = intify(require(req.data, 'project'))
        proj = proj_exist(proj)
        if not proj:
            return FAIL

        if not is_role(req.user, proj, 'supermaster'):
            return FAIL

        inv = invitation_exist(proj, DEFAULT_INVITED_ROLE)

        if inv:
            inv.invitation = gen_invitation()
        else:
            inv = ProjectInvitationAssociation.objects.create(
                project=proj,
                role=DEFAULT_INVITED_ROLE,
                invitation=gen_invitation()
            )

        return Response({
            'code': 0,
            'data': {
                'invitation': inv.invitation
            }
        })


    @action(detail=False, methods=['POST'])
    def get_invitation(self, req: Request):
        proj = intify(require(req.data, 'project'))
        proj = proj_exist(proj)
        if not proj:
            return FAIL

        if not is_role(req.user, proj, 'supermaster'):
            return FAIL

        inv = invitation_exist(proj, DEFAULT_INVITED_ROLE)
        if not inv:
            inv = create_inv(proj, DEFAULT_INVITED_ROLE)

        return Response({
            'code': 0,
            'data': {
                'invitation': inv.invitation
            }
        })





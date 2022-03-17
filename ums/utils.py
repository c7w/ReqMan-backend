import re
from random import sample
import string

from rest_framework.request import Request
from utils.exceptions import ParamErr
from ums.models import *
from utils.sessions import *
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

def proj_user_assoc(req: Request):
    """
    check
    1. project valid
    2. user valid
    3. user in project

    return a dict of the instances or None in the corresponding field
    """

    proj = intify(require(req.data, 'project'))
    proj = proj_exist(proj)

    user = intify(require(req.data, 'user'))
    user = user_exist(user)

    if not user or not proj:
        return {
            'user': user,
            'proj': proj,
            'relation': None
        }

    relation = in_proj(user, proj)
    return {
        'user': user,
        'proj': proj,
        'relation': relation
    }

def invitation_exist(proj: Project, role: str):
    assert role in Role
    return ProjectInvitationAssociation.objects.filter(
        project=proj,
        role=role
    ).first()

def create_inv(proj: Project, role: str):
    return ProjectInvitationAssociation.objects.create(
        project=proj,
        role=role,
        invitation=gen_invitation()
    )

def renew_inv(inv: ProjectInvitationAssociation):
    inv.invitation = gen_invitation()
    return inv

def gen_invitation():
    while True:
        invitation = ''.join(sample(string.ascii_uppercase + string.digits, 8))
        if not ProjectInvitationAssociation.objects.filter(invitation=invitation).first():
            break
    return invitation

def all_users():
    return User.objects.filter(disabled=False)

def in_proj(user: User, proj: Project):
    return UserProjectAssociation.objects.filter(
        user=user,
        project=proj
    ).first()

def is_role(user: User, proj: Project, role: str):
    assert role in Role
    return UserProjectAssociation.objects.filter(
        user=user,
        project=proj,
        role=role
    ).first()

def email_valid(email: str):
    return re.match(
        r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
        email
    ) is not None

def name_exist(name: str):
    users = User.objects.filter(name__iexact=name)
    for u in users:
        if not u.disabled:
            return u

def email_exist(email: str):
    users = User.objects.filter(email__iexact=email)
    for u in users:
        if not u.disabled:
            return u

def user_exist(id: int):
    users = User.objects.filter(id=id)
    for u in users:
        if not u.disabled:
            return u

def proj_exist(id: int):
    projs = Project.objects.filter(id=id)
    for p in projs:
        if not p.disabled:
            return p

def name_valid(name: str):
    return re.match(
        r"^[a-zA-Z0-9_\-\.]+$",
        name
    ) is not None

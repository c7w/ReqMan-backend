from ums.models import *
import re

def is_role(user: User, proj: Project, role: str):
    assert role in Role
    return UserProjectAssociation.objects.filter(
        user=user,
        project=proj,
        role=role
    ).first is not None

def email_valid(email: str):
    return re.match(
        r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
        email
    ) is not None

def name_exist(name: str):
    users = User.objects.filter(name=name)
    for u in users:
        if not u.disabled:
            return u

def email_exist(email: str):
    users = User.objects.filter(email=email).first()
    for u in users:
        if not u.disabled:
            return u

def name_valid(name: str):
    return re.match(
        r"^[a-zA-Z0-9_\-\.]+$",
        name
    ) is not None

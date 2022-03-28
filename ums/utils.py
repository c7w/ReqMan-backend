import re
from random import sample
import string

from rest_framework.request import Request
from utils.exceptions import ParamErr
from ums.models import (
    Project,
    User,
    UserProjectAssociation,
    ProjectInvitationAssociation,
    Role,
)
from django.forms.models import model_to_dict


def require(lst, attr_name):
    """
    require a field in parameter lst.
    If it does not exist, raise ParamErr
    """
    attr = lst.get(attr_name)
    if not attr:
        raise ParamErr(f"missing {attr_name}.")
    return attr


def intify(inp):
    """
    check input, if input is int, return
    if input is str, turn it into string, if unable to convert, raise ParamErr
    """
    if type(inp) == int:
        return inp

    try:
        return int(inp)
    except ValueError:
        raise ParamErr(f"{inp} cannot be convert to an integer")


def user_to_list(user: User, proj: Project = None):
    """
    convert user instance into a dict
    """

    data = model_to_dict(user, exclude=["password", "disabled", "project"])
    if not proj:
        return data

    relation = UserProjectAssociation.objects.filter(project=proj, user=user).first()

    if not relation:
        # note this SHOULD NEVER HAPPEN, but it should run anyway
        print("getting relation for non-existing user")
        return data

    data["role"] = relation.role
    return data


def proj_to_list(proj: Project):
    """
    convert project instance into a dict
    """
    return model_to_dict(proj, exclude=["disabled"])


def proj_user_assoc(req: Request):
    """
    require and check project, user, relation fields in request
    1. project valid
    2. user valid
    3. user in project

    return a dict of the instances or None in the corresponding field
    """

    proj = intify(require(req.data, "project"))
    proj = proj_exist(proj)

    user = intify(require(req.data, "user"))
    user = user_exist(user)

    if not user or not proj:
        return {"user": user, "proj": proj, "relation": None}

    relation = in_proj(user, proj)
    return {"user": user, "proj": proj, "relation": relation}


def invitation_exist(proj: Project, role: str):
    """
    check the pair (proj, role)
    if exist, return the ProjectInvitationAssociation instance
    if not, return None
    """
    assert role in Role
    return ProjectInvitationAssociation.objects.filter(project=proj, role=role).first()


def create_inv(proj: Project, role: str):
    """
    create a ProjectInvitationAssociation
    """
    return ProjectInvitationAssociation.objects.create(
        project=proj, role=role, invitation=gen_invitation()
    )


def renew_inv(inv: ProjectInvitationAssociation):
    """
    create a ProjectInvitationAssociation
    """
    inv.invitation = gen_invitation()
    inv.save()
    return inv


def gen_invitation():
    """
    generate the invitation string and return it
    """
    while True:
        invitation = "".join(sample(string.ascii_uppercase + string.digits, 8))
        if not ProjectInvitationAssociation.objects.filter(
            invitation=invitation
        ).first():
            break
    return invitation


def all_users():
    """
    return all users, filtered the disabled ones
    """
    return User.objects.filter(disabled=False)


def in_proj(user: User, proj: Project):
    """
    check if user in project
    if true, return UserProjectAssociation instance
    else return None
    """
    return UserProjectAssociation.objects.filter(user=user, project=proj).first()


def is_role(user: User, proj: Project, role: str):
    """
    check if user in project with specific role
    if true, return UserProjectAssociation instance
    else return None
    """
    assert role in Role
    return UserProjectAssociation.objects.filter(
        user=user, project=proj, role=role
    ).first()


def email_valid(email: str):
    """
    check if email valid
    """
    return (
        re.match(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email)
        is not None
    )


def name_exist(name: str):
    """
    check if name exist, NOT case sensitive
    return user instance if possible
    """
    users = User.objects.filter(name__iexact=name)
    for u in users:
        if not u.disabled:
            return u


def email_exist(email: str):
    """
    check if email exist, NOT case sensitive
    return user instance if possible
    """
    users = User.objects.filter(email__iexact=email)
    for u in users:
        if not u.disabled:
            return u


def user_exist(id: int):
    """
    check if user exist, NOT case sensitive
    return user instance if possible
    """
    users = User.objects.filter(id=id)
    for u in users:
        if not u.disabled:
            return u


def proj_exist(id: int):
    """
    check if project exist, NOT case sensitive
    return project instance if possible
    """
    projs = Project.objects.filter(id=id)
    for p in projs:
        if not p.disabled:
            return p


def name_valid(name: str):
    """
    check if name valid
    """
    return re.match(r"^[a-zA-Z0-9_]{3,16}$", name) is not None

import re
from random import sample
import string
from functools import wraps
import humanize

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
import smtplib
from email.mime.text import MIMEText
import hashlib
from utils.model_date import get_timestamp
from ums.models import *

EMAIL_EXPIRE_SECONDS = 3600
RESETTING_STATUS_EXPIRE_SECONDS = 3000
EMAIL_MIN_INTERVAL = 30


def require(lst, attr_name, attr_type=None):
    """
    require a field in parameter lst.
    If it does not exist, raise ParamErr
    """
    attr = lst.get(attr_name)
    if attr is None:
        raise ParamErr(f"missing {attr_name}.")

    if attr_type == int:
        return intify(attr)

    if attr_type == float:
        return floatify(attr)

    if attr_type == bool:
        return booleanfy(attr)

    if attr_type == list and type(attr) != list:
        raise ParamErr(
            f"Expecting array for {attr_name}, got {type(attr)} instead, '{attr_name}' = {attr}"
        )

    return attr


def floatify(inp):
    """
    check input, if input is int, return
    if input is str, turn it into string, if unable to convert, raise ParamErr
    """
    if type(inp) == float:
        return inp

    try:
        return float(inp)
    except ValueError:
        raise ParamErr(f"{inp} cannot be convert to an float")


def booleanfy(inp):
    """
    check input, if input is int, return
    if input is str, turn it into string, if unable to convert, raise ParamErr
    """
    if type(inp) == bool:
        return inp

    try:
        return bool(inp)
    except ValueError:
        raise ParamErr(f"{inp} cannot be convert to an bool")


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
    convert user instance into a dict, or contain its role in a single project
    """

    data = model_to_dict(user, exclude=["password", "disabled", "project"])
    minors = UserMinorEmailAssociation.objects.filter(user=user)
    data["minor_emails"] = [(r.email, r.verified) for r in minors]

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
    check if major / minor email exist, NOT case sensitive
    """
    try:
        email = str(email)
    except:
        return None
    users = User.objects.filter(email__iexact=email.lower(), disabled=False)
    minors = UserMinorEmailAssociation.objects.filter(email__iexact=email.lower())
    if len(users) == 0 and len(minors) == 0:
        return False
    return True


def get_user_by_major_email(email: str):
    return User.objects.filter(email=email, disabled=False).first()


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


def user_and_projects(x: User):
    """
    convert user object to a list, include all the projects and its roles respectively
    """
    return {
        "user": user_to_list(x),
        "projects": [
            {
                **model_to_dict(r.project, exclude=["disabled"]),
                "role": r.role,
            }
            for r in UserProjectAssociation.objects.filter(user=x)
        ],
        # "avatar": x.avatar,
    }


def send_mail(receiver: str, content: str = "", subject: str = "") -> bool:
    """
    send an email in the name of ReqMan
    """
    if content == "":
        content = """
        the content of this email has not been configured yet ...
        maybe you can contact the administrator for help.
        """

    if subject == "":
        subject = "subject not yet configured"

    try:
        username = Config.objects.filter(key="email_username").first().value
        host = Config.objects.filter(key="email_host").first().value
        auth = Config.objects.filter(key="email_auth").first().value
    except Exception as e:
        print(
            "fail to load email sending config from db, use default. Error Message:",
            e.__str__(),
        )
        username = "reqman@foxmail.com"
        host = "smtp.qq.com"
        auth = "ousjljeyregndcab"

    msg = MIMEText(content, "html")
    msg["From"] = f"ReqMan<{username}>"
    msg["Subject"] = subject
    msg["To"] = receiver

    try:
        server = smtplib.SMTP_SSL(host, 465)
        server.login(username, auth)
        server.sendmail(username, [receiver], msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e.__str__())
        return False


def email_password_reset(email: str, hash1: str):
    try:
        template = Config.objects.filter(key="reset_email_template").first().value
        title = Config.objects.filter(key="reset_email_title").first().value
        url = Config.objects.filter(key="front_url").first().value.strip("/")
        humanize.i18n.activate("zh_CN")
        expire = humanize.naturaldelta(EMAIL_EXPIRE_SECONDS)
        template = key_render(
            template, {"front_url": url, "expire": expire, "hash1": hash1}
        )
    except Exception as e:
        print("Fail to load template, use default. Error Message:", e.__str__())
        template = f"Your hash1 to modify password is {hash1}, it will be expired in {EMAIL_EXPIRE_SECONDS}."
        title = "ReqMan: Password Reset"
    return send_mail(email, template, title)


def key_render(template: str, dic: dict):
    for k, v in dic.items():
        template = template.replace(f"<{k}>", v)
    return template


def email_verify(email: str, _hash: str):
    try:
        template = Config.objects.filter(key="verify_email_template").first().value
        title = Config.objects.filter(key="verify_email_title").first().value
        url = Config.objects.filter(key="front_url").first().value.strip("/")
        humanize.i18n.activate("zh_CN")
        expire = humanize.naturaldelta(EMAIL_EXPIRE_SECONDS)
        template = key_render(
            template, {"front_url": url, "expire": expire, "hash": _hash}
        )
    except Exception as e:
        print("Fail to load template, use default. Error Message:", e.__str__())
        template = f"Your hash to verify email is {_hash}, it will be expired in {EMAIL_EXPIRE_SECONDS}."
        title = "ReqMan: Email Verify"

    return send_mail(email, template, title)


def new_verify_email(user: User, email: str, major: bool = False):
    """
    check user's email sending frequency and send out verify email
    """
    hashcode = hashlib.sha256(str(get_timestamp()).encode()).hexdigest()
    now = get_timestamp()

    # frequency check
    recent = PendingVerifyEmail.objects.filter(user=user).order_by("-createdAt").first()
    if recent and (now - recent.createdAt) < EMAIL_MIN_INTERVAL:
        return False, "freq_exceed"

    # new record
    PendingVerifyEmail.objects.filter(
        user=user, email=email
    ).delete()  # previous should be removed
    PendingVerifyEmail.objects.create(
        user=user, email=email, hash=hashcode, is_major=major
    )
    return email_verify(email, hashcode), "mail"

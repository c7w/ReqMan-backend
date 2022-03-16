from ums.models import User
import re

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

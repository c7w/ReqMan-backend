from ums.models import User
import re

def email_valid(email: str):
    return re.match(
        r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
        email
    ) is not None

def name_dup(name: str):
    usr = User.objects.filter(name=name).first()
    return usr is not None

def email_dup(email: str):
    usr = User.objects.filter(email=email).first()
    return usr is not None

from ums.models import User
import re

def email_valid(email: str):
    return re.match(
        r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
        email
    ) is not None

def name_exist(name: str):
    usr = User.objects.filter(name=name).first()
    return usr

def email_exist(email: str):
    usr = User.objects.filter(email=email).first()
    return usr

def name_valid(name: str):
    return re.match(
        r"^[a-zA-Z0-9_\-\.]+$",
        name
    ) is not None

from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from ums.utils import is_role, in_proj, intify, require, proj_exist
from ums.models import Role
from functools import wraps
from utils.exceptions import ParamErr, Failure

rights = {}


def project_rights(role):
    def decorator(func):
        rights[func.__name__] = {"type": "project", "role": role}

        @wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        return wrapper

    return decorator


class GeneralPermission(BasePermission):
    def has_permission(self, req, view):
        if view.action not in rights:
            return True
        pm = rights[view.action]
        # check project - user rights
        if pm["type"] == "project":
            if not req.user:
                return False
            proj = intify(require(req.data, "project"))
            proj = proj_exist(proj)
            if not proj:
                raise ParamErr("proj non-exist")

            if pm["role"] == "AnyMember":
                relation = in_proj(req.user, proj)
            else:
                assert pm["role"] in Role
                relation = is_role(req.user, proj, pm["role"])

            if not relation:
                return False

            req.auth["proj"] = proj
            req.auth["relation"] = relation
            return True
        return True

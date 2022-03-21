from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from ums.utils import is_role, in_proj, intify, require
from ums.models import Role

class SupermasterOfProj(BasePermission):
    def has_permission(self, req, view):
        if not req.user:
            return False
        proj = intify(require(req.data, 'project'))
        if not is_role(req.user, proj, Role.SUPERMASTER):
            return False
        return True

class AnyMemberOfProj(BasePermission):
    def has_permission(self, req, view):
        if not req.user:
            return False
        proj = intify(require(req.data, 'project'))
        if not in_proj(req.user, proj):
            return False
        return True

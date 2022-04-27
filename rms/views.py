from asyncio import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from ums.views import FAIL
from ums.views import SUCC
from utils.sessions import SessionAuthentication
from ums.utils import *
from rms.utils import *
from rest_framework import exceptions


class RMSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    def projectGET(self, req: Request):
        proj = intify(require(req.query_params, "project"))
        proj = proj_exist(proj)
        if not proj:
            return FAIL
        if not in_proj(req.user, proj):
            return FAIL
        type = require(req.query_params, "type")

        resu = []
        if type == "ir":
            resu = serialize(getIR(proj), ["SR"])
        elif type == "sr":
            if (
                not is_role(req.user, proj, Role.SYS)
                and not is_role(req.user, proj, Role.SUPERMASTER)
                and not is_role(req.user, proj, Role.DEV)
                and not is_role(req.user, proj, Role.QA)
                and not is_role(req.user,proj,Role.MEMBER)
            ):
                raise exceptions.PermissionDenied
            resu = serialize(getSR(proj), ["IR"])
        elif type == "iteration":
            resu = serialize(getIeration(proj))
        elif type == "ir-sr":
            resu = serialize(getIRSR(proj))
        elif type == "sr-iteration":
            resu = serialize(getSRIteration(proj))
        elif type == "service":
            resu = serialize(getService(proj))
        elif type == "user-iteration":
            resu = serialize(getUserIteration(proj))
        elif type == "service-sr":
            resu = serialize(getServiceSR(proj))
        elif type == "serviceOfSR":
            SRId = intify(require(req.query_params, "SRId"))
            judgeTypeInt(SRId)
            resu = serialize(getServiceOfSR(proj, SRId))
        elif type == "SROfService":
            serviceId = intify(require(req.query_params, "serviceId"))
            judgeTypeInt(serviceId)
            resu = serialize(getSROfService(proj, serviceId), ["IR"])
        elif type == "ir-iteration":
            resu = serialize(getIRIteration(proj))
        elif type == "project-iteration":
            resu = serialize(getProjectIteration(proj))
        elif type == "SR_changeLog":
            srId = intify(require(req.query_params, "SRId"))
            judgeTypeInt(srId)
            resu = serialize(getSRChangeLog(srId))
        elif type == "user-sr":
            resu = serialize(getUserSR(proj))
        else:
            return FAIL
        return Response({"code": 0, "data": resu})

    def projectPOST(self, req: Request):
        proj = intify(require(req.data, "project"))
        proj = proj_exist(proj)
        if not proj:
            raise ParamErr(f"No project")

        operation = require(req.data, "operation")

        type = require(req.data, "type")
        typeAll = [
            "ir",
            "sr",
            "sr-iteration",
            "iteration",
            "user-iteration",
            "service",
            "service-sr",
        ]
        # if type == 'ir' or type == 'sr' or type == 'sr-iteration' or type=='iteration':
        if type in typeAll:
            if not is_role(req.user, proj, Role.SUPERMASTER) and not is_role(
                req.user, proj, Role.SYS
            ):
                raise exceptions.PermissionDenied
        if type == "SRState":
            if (
                not is_role(req.user, proj, Role.SYS)
                and not is_role(req.user, proj, Role.SUPERMASTER)
                and not is_role(req.user, proj, Role.DEV)
                and not is_role(req.user, proj, Role.QA)
            ):
                raise exceptions.PermissionDenied
        isFail = False
        if operation == "create":
            isFail = createOperation(proj, type, req.data, req.user)
        elif operation == "update":
            isFail = updateOperation(proj, type, req.data, req.user)
        if operation == "delete":
            isFail = deleteOperation(proj, type, req.data)
        if isFail:
            return FAIL
        else:
            return SUCC

    @action(detail=False, methods=["POST", "GET"])
    def project(self, req: Request):
        if req.method == "POST":
            return RMSViewSet.projectPOST(self, req)
        elif req.method == "GET":
            return RMSViewSet.projectGET(self, req)

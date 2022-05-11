import sre_parse
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
from rdts.models import *
from rest_framework import exceptions
from utils.permissions import project_rights, GeneralPermission
from rdts.utlis import pagination
from django.db.models import OuterRef, Subquery, Q


class RMSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [GeneralPermission]

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
                and not is_role(req.user, proj, Role.MEMBER)
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
            if (
                not is_role(req.user, proj, Role.SUPERMASTER)
                and not is_role(req.user, proj, Role.SYS)
                and not is_role(req.user, proj, Role.QA)
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

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_sr(self, req: Request):
        from_num = require(req.query_params, "from", int)
        size = require(req.query_params, "size", int)

        def _add_ir(x):
            ir = x.IR.filter(disabled=False).first()
            return {"IR": ir.id if ir else None}

        return Response(
            pagination(
                SR.objects.filter(project=req.auth["proj"], disabled=False),
                from_num,
                size,
                exclude=["IR", "disabled"],
                addon=_add_ir,
            )
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_single_sr(self, req: Request):
        sr_id = require(req.query_params, "id", int)
        sr = SR.objects.filter(
            disabled=False, project=req.auth["proj"], id=sr_id
        ).first()
        if sr:
            ir = sr.IR.filter(disabled=False)
            commits = CommitSRAssociation.objects.filter(SR=sr).all()
            issues = IssueSRAssociation.objects.filter(SR=sr).all()
            mrs = MRSRAssociation.objects.filter(SR=sr).all()

            return Response(
                {
                    "code": 0,
                    "data": {
                        **model_to_dict(sr, exclude=["IR", "disabled"]),
                        "IR": [model_to_dict(i, exclude=["disabled"]) for i in ir],
                        "commit": [
                            [
                                model_to_dict(c.commit, exclude=["disabled"]),
                                c.auto_added,
                            ]
                            for c in commits
                        ],
                        "issue": [
                            [model_to_dict(c.issue), c.auto_added] for c in issues
                        ],
                        "mr": [[model_to_dict(c.MR), c.auto_added] for c in mrs],
                    },
                }
            )

        return FAIL

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def search_sr(self, req: Request):
        title_only = require(req.data, "title_only", bool)
        kw = require(req.data, "kw", str)
        limit = require(req.data, "limit", int)
        vals = ("id", "title", "description", "state", "createdBy", "createdAt")
        if title_only:
            res = (
                SR.objects.filter(project=req.auth["proj"], disabled=False)
                .filter(title__contains=kw)
                .order_by("-createdAt")
                .values(*vals)[:limit]
            )
        else:
            res = (
                SR.objects.filter(project=req.auth["proj"], disabled=False)
                .filter(Q(title__contains=kw) | Q(description__contains=kw))
                .order_by("-createdAt")
                .values(*vals)[:limit]
            )

        return Response({"code": 0, "data": res})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def dashboard(self, req: Request):
        limit = require(req.query_params, "limit", int)

        if limit > 10:
            limit = 10

        wip = [
            model_to_dict(s, exclude=["IR"])
            for s in SR.objects.filter(
                usersrassociation__user=req.user,
                project=req.auth["proj"],
                state=SR.SRState.WIP,
                disabled=False,
            ).order_by("-priority", "-createdAt")[:limit]
        ]

        todo = [
            model_to_dict(s, exclude=["IR"])
            for s in SR.objects.filter(
                usersrassociation__user=req.user,
                project=req.auth["proj"],
                state=SR.SRState.TODO,
                disabled=False,
            ).order_by("-priority", "-createdAt")[:limit]
        ]

        reviewing = [
            model_to_dict(s, exclude=["IR"])
            for s in SR.objects.filter(
                usersrassociation__user=req.user,
                project=req.auth["proj"],
                state=SR.SRState.Reviewing,
                disabled=False,
            ).order_by("-priority", "-createdAt")[:limit]
        ]

        return Response(
            {"code": 0, "data": {"wip": wip, "todo": todo, "reviewing": reviewing}}
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def get_iteration_digest(self, req: Request):
        it = require(req.query_params, "iteration", int)
        SRs = SRIterationAssociation.objects.filter(
            iteration_id=it,
            iteration__project=req.auth["proj"],
            iteration__disabled=False,
            SR__disabled=False,
            SR__project=req.auth["proj"],
        ).values("SR_id")
        bug_count = Issue.objects.filter(
            repo__disabled=False,
            repo__project=req.auth["proj"],
            is_bug=True,
            issuesrassociation__SR__in=map(lambda x: x["SR_id"], SRs),
        ).count()
        return Response(
            {"code": 0, "data": {"bug_count": bug_count, "SR_count": len(SRs)}}
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def get_ir_sr(self, req: Request):
        ir = require(req.query_params, "ir", int)
        SRs = SR.objects.filter(
            irsrassociation__IR__id=ir,
            irsrassociation__IR__project=req.auth["proj"],
            irsrassociation__IR__disabled=False,
            disabled=False,
            project=req.auth["proj"],
        ).values(
            "id", "title", "description", "priority", "state", "createdBy", "createdAt"
        )
        return Response({"code": 0, "data": SRs})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def get_service_sr(self, req: Request):
        service = require(req.query_params, "service", int)
        SRs = SR.objects.filter(
            servicesrassociation__service__id=service,
            servicesrassociation__service__project=req.auth["proj"],
            servicesrassociation__service__disabled=False,
            disabled=False,
            project=req.auth["proj"],
        ).values(
            "id", "title", "description", "priority", "state", "createdBy", "createdAt"
        )
        return Response({"code": 0, "data": SRs})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def get_iteration_sr(self, req: Request):
        it = require(req.query_params, "iteration", int)
        SRs = SR.objects.filter(
            sriterationassociation__iteration__id=it,
            sriterationassociation__iteration__project=req.auth["proj"],
            sriterationassociation__iteration__disabled=False,
            disabled=False,
            project=req.auth["proj"],
        ).values(
            "id", "title", "description", "priority", "state", "createdBy", "createdAt"
        )
        return Response({"code": 0, "data": SRs})

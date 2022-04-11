from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rdts.utlis import *
from rdts.models import *
from ums.models import Role
from ums.utils import in_proj, intify, is_role, proj_exist, require
from ums.views import FAIL, SUCC, STATUS
from utils.sessions import SessionAuthentication
from utils.permissions import GeneralPermission, project_rights
from rest_framework.decorators import action
from rms.utils import serialize
from rdts.query_class import type_map
import json
from django.forms.models import model_to_dict


class RDTSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [GeneralPermission]

    def projectGET(self, req: Request):
        resu = []
        type = require(req.query_params, "type")
        if type == "repo":
            projectId = intify(require(req.query_params, "project"))
            proje = proj_exist(projectId)
            if not proje:
                return FAIL
            if not in_proj(req.user, proje):
                return FAIL
            resu = serialize(getRepo(proje))
            return Response({"code": 0, "data": resu})
        repo = intify(require(req.query_params, "repo"))
        repo = repoExist(repo)
        if not repo:
            return FAIL
        if type == "mr":
            resu = serialize(getMR(repo))
        elif type == "commit":
            resu = serialize(getCommit(repo))
        elif type == "issue":
            resu = serialize(getIssue(repo))
        elif type == "commit-sr":
            resu = serialize(getCommitSR(repo))
        elif type == "mr-sr":
            resu = serialize(getMRSR(repo))
        elif type == "issue-sr":
            resu = serialize(getIssueSR(repo))
        elif type == "issue-mr":
            issueId = intify(require(req.query_params, "issueId"))
            resu = serialize(getIssueMR(issueId))
        else:
            return FAIL
        return Response({"code": 0, "data": resu})

    def projectPOST(self, req: Request):
        type = require(req.data, "type")
        proj = intify(require(req.data, "project"))
        proj = proj_exist(proj)

        if (not is_role(req.user, proj, Role.SYS)) and (
            not is_role(req.user, proj, Role.SUPERMASTER)
        ):
            return FAIL

        operation = require(req.data, "operation")
        fail = True
        if operation == "create":
            fail = createOpertion(proj, type, req.data, req.user)
        elif operation == "update":
            fail = updateOperation(proj, type, req.data)
        elif operation == "delete":
            fail = deleteOperation(proj, type, req.data)
        if not fail:
            return SUCC
        else:
            return FAIL

    @action(detail=False, methods=["GET", "POST"], url_path="project")
    def rdts_project(self, req: Request):
        if req.method == "POST":
            return self.projectPOST(req)
        elif req.method == "GET":
            return self.projectGET(req)
        else:
            return FAIL

    @project_rights(Role.SUPERMASTER)
    @action(detail=False, methods=["POST"])
    def repo_op(self, req: Request):

        proj = req.auth["proj"]
        repo_type = require(req.data, "type")
        remote_id = require(req.data, "remote_id")
        access_token = require(req.data, "access_token")
        enable_crawling = require(req.data, "enable_crawling", bool)
        info = require(req.data, "info")
        title = require(req.data, "title")
        desc = require(req.data, "description")
        op = require(req.data, "op")

        if repo_type not in type_map:
            raise ParamErr("unsupported repo type")

        if len(title) > 255:
            return STATUS(1)

        if len(desc) > 1000:
            return STATUS(2)

        if op == "add":
            repo = Repository.objects.create(
                project=proj, title=title, description=desc, createdBy=req.user
            )
            RemoteRepo.objects.create(
                type=repo_type,
                remote_id=remote_id,
                access_token=access_token,
                enable_crawling=enable_crawling,
                info=json.dumps(info, ensure_ascii=False),
                repo=repo,
            )
            return SUCC

        if op == "modify":
            repo_id = require(req.data, "id", int)
            repo = Repository.objects.filter(id=repo_id, disabled=False)
            if len(repo) == 0:
                return STATUS(3)

            remote_repo = RemoteRepo.objects.filter(repo=repo[0])

            repo.update(title=title, description=desc)
            remote_repo.update(
                type=repo_type,
                remote_id=remote_id,
                access_token=access_token,
                enable_crawling=enable_crawling,
                info=json.dumps(info, ensure_ascii=False),
                repo=repo,
            )
            return SUCC

        raise ParamErr("invalid op")

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def repo_crawllog(self, req: Request):
        repo = require(req.data, "repo", int)
        page = require(req.data, "page", int)
        PAGE_SZ = 50
        offset = (page - 1) * PAGE_SZ
        end = page * PAGE_SZ

        if offset < 0 or end < 0 or offset > end:
            raise ParamErr(f"page number error [{offset}, {end}]")

        repo = Repository.objects.filter(id=repo, disabled=False).first()
        if not repo or repo.project.id != req.auth["proj"].id:
            return STATUS(3)

        remote_repo = RemoteRepo.objects.filter(repo=repo).first()

        logs = CrawlLog.objects.filter(repo=remote_repo).order_by("-time")[offset:end]

        print(logs)
        return Response({"code": 0, "data": [model_to_dict(log) for log in logs]})

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def crawl_detail(self, req: Request):
        crawl = require(req.data, "crawl_id", int)

        log = CrawlLog.objects.filter(id=crawl).first()
        if not log:
            return STATUS(1)

        if log.repo.repo.project.id != req.auth["proj"].id:
            return STATUS(1)

        issues = IssueCrawlAssociation.objects.filter(crawl=log)
        mrs = MergeCrawlAssociation.objects.filter(crawl=log)
        commits = CommitCrawlAssociation.objects.filter(crawl=log)

        return Response(
            {
                "code": 0,
                "data": {
                    "issue": [
                        model_to_dict(
                            i.issue,
                            fields=[
                                "issue_id",
                                "title",
                                "labels",
                                "authoredByUserName",
                            ],
                        )
                        for i in issues
                    ],
                    "merge": [
                        model_to_dict(
                            m.merge, fields=["merge_id", "title", "authoredByUserName"]
                        )
                        for m in mrs
                    ],
                    "commit": [
                        model_to_dict(
                            c.commit, fields=["hash_id", "title", "commiter_name"]
                        )
                        for c in commits
                    ],
                },
            }
        )

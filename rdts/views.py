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
from rest_framework.decorators import api_view
import hashlib
from utils.model_date import get_timestamp
from rest_framework import exceptions
from func_timeout import func_set_timeout, FunctionTimedOut
from rdts.query_class import Gitlab, type_map
from django.db.models import Q


@api_view(["POST"])
def webhook(req: Request):
    token = req.META.get("HTTP_X_GITLAB_TOKEN")
    print(token)

    if not token:
        return FAIL

    remote = RemoteRepo.objects.filter(
        repo__disabled=False, secret_token=token.strip()
    ).first()

    if not remote:
        return FAIL

    if "object_kind" in req.data and req.data["object_kind"] in [
        "push",
        "merge_request",
        "issue",
    ]:
        PendingWebhookRequests.objects.create(
            remote=remote, body=json.dumps(req.data, ensure_ascii=False)
        )

    return SUCC


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

            resu = []
            repos = getRepo(proje)
            for repo in repos:
                remote = RemoteRepo.objects.filter(repo=repo).first()
                resu += [
                    {
                        **model_to_dict(repo),
                        "remote": model_to_dict(remote) if remote else None,
                    }
                ]

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

        if type == "mr-sr" or type == "issue-mr":
            if not is_role(req.user, proj, Role.SUPERMASTER) and not is_role(
                req.user, proj, Role.QA
            ):
                raise exceptions.PermissionDenied
        if type == "repo":
            if not is_role(req.user, proj, Role.SUPERMASTER):
                raise exceptions.PermissionDenied

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

        if "base_url" not in info:
            return STATUS(4)

        remote_url = (
            info["base_url"]
            .strip()
            .strip("/")
            .replace("http://", "")
            .replace("https://", "")
        )

        if op == "add":
            secret_token = hashlib.sha3_512(str(get_timestamp()).encode()).hexdigest()
            repo = Repository.objects.create(
                project=proj,
                title=title,
                description=desc,
                createdBy=req.user,
                url=remote_url,
            )
            RemoteRepo.objects.create(
                type=repo_type,
                remote_id=remote_id,
                access_token=access_token,
                enable_crawling=enable_crawling,
                info=json.dumps(info, ensure_ascii=False),
                repo=repo,
                secret_token=secret_token,
            )
            return SUCC

        if op == "modify":
            repo_id = require(req.data, "id", int)
            repo = Repository.objects.filter(
                id=repo_id, disabled=False, project=req.auth["proj"]
            )
            if len(repo) == 0:
                return STATUS(3)

            remote_repo = RemoteRepo.objects.filter(repo=repo[0])

            repo.update(title=title, description=desc, url=remote_url)
            remote_repo.update(
                type=repo_type,
                remote_id=remote_id,
                access_token=access_token,
                enable_crawling=enable_crawling,
                info=json.dumps(info, ensure_ascii=False),
                repo=repo.first(),
            )
            return SUCC

        raise ParamErr("invalid op")

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def repo_crawllog(self, req: Request):
        repo = require(req.query_params, "repo", int)
        page = require(req.query_params, "page", int)
        PAGE_SZ = 50
        offset = (page - 1) * PAGE_SZ
        end = page * PAGE_SZ

        if offset < 0 or end < 0 or offset > end:
            raise ParamErr(f"page number error [{offset}, {end}]")

        repo = Repository.objects.filter(
            id=repo, disabled=False, project=req.auth["proj"]
        ).first()
        if not repo or repo.project.id != req.auth["proj"].id:
            return STATUS(1)

        remote_repo = RemoteRepo.objects.filter(repo=repo).first()

        logs = CrawlLog.objects.filter(repo=remote_repo).order_by("-time")[offset:end]

        return Response(
            {"code": 0, "data": [model_to_dict(log, exclude=["repo"]) for log in logs]}
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def crawl_detail(self, req: Request):
        crawl = require(req.query_params, "crawl_id", int)
        page = require(req.query_params, "page", int)
        PAGE_SZ = 20

        begin = (page - 1) * PAGE_SZ
        end = page * PAGE_SZ

        if begin < 0 or end < 0 or begin > end:
            return STATUS(2)

        log = CrawlLog.objects.filter(id=crawl).first()
        if not log:
            return STATUS(1)

        if log.repo.repo.project.id != req.auth["proj"].id:
            return STATUS(1)

        issues = IssueCrawlAssociation.objects.filter(crawl=log)[begin:end]
        mrs = MergeCrawlAssociation.objects.filter(crawl=log)[begin:end]
        commits = CommitCrawlAssociation.objects.filter(crawl=log)[begin:end]

        return Response(
            {
                "code": 0,
                "data": {
                    "log": model_to_dict(log),
                    "issue": [
                        {
                            **model_to_dict(
                                i.issue,
                                fields=[
                                    "issue_id",
                                    "title",
                                    "labels",
                                    "authoredByUserName",
                                ],
                            ),
                            "op": i.operation,
                        }
                        for i in issues
                    ],
                    "merge": [
                        {
                            **model_to_dict(
                                m.merge,
                                fields=["merge_id", "title", "authoredByUserName"],
                            ),
                            "op": m.operation,
                        }
                        for m in mrs
                    ],
                    "commit": [
                        {
                            **model_to_dict(
                                c.commit, fields=["hash_id", "title", "commiter_name"]
                            ),
                            "op": c.operation,
                        }
                        for c in commits
                    ],
                },
            }
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def get_recent_activity(self, req: Request):
        digest = require(req.data, "digest", bool)
        dev_id = require(req.data, "dev_id", list)
        limit = require(
            req.data,
            "limit",
        )

        ACTIVITY_LIMIT = 20

        if limit == -1:
            begin = 0
        else:
            begin = now() - limit

        info = []

        d_commits = {}
        d_merges = {}
        d_issues = {}

        for did in dev_id:
            dev = User.objects.filter(id=did, disabled=False).values("id")
            if len(dev) == 0:
                return STATUS(1)

            relation = UserProjectAssociation.objects.filter(
                project=req.auth["proj"], user__id=did
            ).count()
            if relation == 0:
                return STATUS(1)

            d_commits[did] = []
            d_issues[did] = []
            d_merges[did] = []

        if digest:
            merges = MergeRequest.objects.filter(
                user_authored__in=dev_id,
                authoredAt__gte=begin,
                repo__project=req.auth["proj"],
                repo__disabled=False,
            ).values("authoredAt", "user_authored")
            for m in merges:
                d_merges[m["user_authored"]] += [m]

            commits = Commit.objects.filter(
                user_committer__in=dev_id,
                createdAt__gte=begin,
                repo__project=req.auth["proj"],
                repo__disabled=False,
            ).values("additions", "deletions", "createdAt", "title", "user_committer")
            for c in commits:
                d_commits[c["user_committer"]] += [c]

            issues = Issue.objects.filter(
                user_assignee__in=dev_id,
                closedAt__gte=begin,
                repo__project=req.auth["proj"],
                repo__disabled=False,
            ).values("closedAt", "authoredAt", "user_assignee")
            for i in issues:
                d_issues[i["user_assignee"]] += [i]

        else:
            for did in dev_id:
                # here we do not strictly limit the role to issue
                # if relation.role != Role.DEV:
                #     return STATUS(1)
                merges = (
                    MergeRequest.objects.filter(
                        Q(user_authored__id=did) | Q(user_reviewed__id=did)
                    )
                    .filter(
                        authoredAt__gte=begin,
                        repo__project=req.auth["proj"],
                        repo__disabled=False,
                    )
                    .order_by("-authoredAt")
                    .values(
                        "id",
                        "merge_id",
                        "title",
                        "description" "repo",
                        "url",
                        "authoredAt",
                        "reviewedAt",
                        "user_authored",
                        "user_reviewed",
                    )[:ACTIVITY_LIMIT]
                )
                commits = (
                    Commit.objects.filter(
                        user_committer__id=did,
                        createdAt__gte=begin,
                        repo__project=req.auth["proj"],
                        repo__disabled=False,
                    )
                    .order_by("-createdAt")
                    .values(
                        "id",
                        "hash_id",
                        "repo",
                        "title",
                        "createdAt",
                        "user_committer",
                        "additions",
                        "deletions",
                    )[:ACTIVITY_LIMIT]
                )
                issues = (
                    Issue.objects.filter(
                        Q(user_closed__id=did) | Q(user_authored__id=did)
                    )
                    .filter(
                        user_assignee__id=did,
                        closedAt__gte=begin,
                        repo__project=req.auth["proj"],
                        repo__disabled=False,
                        is_bug=True,
                    )
                    .order_by("-closedAt")
                    .values(
                        "id",
                        "issue_id",
                        "repo",
                        "title",
                        "description" "authoredAt",
                        "closedAt",
                        "user_authored",
                        "user_closed",
                    )[:ACTIVITY_LIMIT]
                )

                info += [(did, merges, commits, issues)]

        if digest:
            # lines = [0, 0, 0, 0, 0, 0]
            res = []
            for did in dev_id:
                merges = d_merges[did]
                commits = d_commits[did]
                issues = d_issues[did]
                additions = sum([c["additions"] for c in commits])
                deletions = sum([c["deletions"] for c in commits])
                personal_lines = [c["additions"] + c["deletions"] for c in commits]
                # for c in commits:
                #     delta = c["additions"] + c["deletions"]
                #     personal_lines += [delta]
                #     delta = delta // 100
                #     if delta > 5:
                #         # print(c["title"], c["additions"], c["deletions"])
                #         delta = 5
                #     lines[delta] += 1

                res += [
                    {
                        "mr_count": len(merges),
                        "commit_count": len(commits),
                        "additions": additions,
                        "deletions": deletions,
                        "issue_count": len(issues),
                        "issue_times": [
                            round(i["closedAt"] - i["authoredAt"]) for i in issues
                        ],
                        "commit_times": [round(c["createdAt"]) for c in commits],
                        "mr_times": [round(m["authoredAt"]) for m in merges],
                        "commit_lines": personal_lines,
                    }
                ]
            return Response({"code": 0, "data": res})
        else:
            res = []
            for dev, merges, commits, issues in info:
                res += [
                    {
                        "merges": merges,
                        "commits": commits,
                        "issues": issues,
                    }
                ]
            return Response({"code": 0, "data": res})

    @project_rights([Role.QA, Role.SUPERMASTER])
    @action(detail=False, methods=["GET"])
    def iteration_bugs(self, req: Request):
        iteration_id = require(req.query_params, "iteration", int)
        iteration = Iteration.objects.filter(
            id=iteration_id, project=req.auth["proj"]
        ).first()
        if not iteration:
            return FAIL
        relations = SRIterationAssociation.objects.filter(iteration=iteration)
        bugs = []
        for r in relations:
            issues = IssueSRAssociation.objects.filter(SR=r.SR, issue__is_bug=True)
            bugs += [(i.issue, r.SR) for i in issues]

        return Response(
            {
                "code": 0,
                "data": {
                    "bug_issues": [
                        {
                            **model_to_dict(
                                i,
                                fields=[
                                    "id",
                                    "issue_id",
                                    "title",
                                    "description",
                                    "authoredAt",
                                    "closedAt",
                                    "url",
                                ],
                            ),
                            "sr": model_to_dict(
                                sr,
                                fields=[
                                    "id",
                                    "title",
                                    "description",
                                    "priority",
                                    "rank",
                                ],
                            ),
                        }
                        for i, sr in bugs
                    ]
                },
            }
        )

    @project_rights([Role.SUPERMASTER])
    @action(detail=False, methods=["GET"])
    def test_access_token(self, req: Request):
        repo = require(req.query_params, "repository", int)
        repo = Repository.objects.filter(id=repo, disabled=False).first()

        if not repo:
            return STATUS(2)

        remote = RemoteRepo.objects.filter(repo=repo).first()

        if not remote:
            return STATUS(2)

        req = type_map[remote.type](
            json.loads(remote.info)["base_url"], remote.remote_id, remote.access_token
        )

        @func_set_timeout(1)
        def send_request():
            return req.project()

        try:
            status, data = send_request()
        except FunctionTimedOut:
            return STATUS(1)
        except:
            return STATUS(3)

        return Response({"code": 0, "data": {"status": status, "response": data}})

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def get_user_activity(self, req: Request):
        digest = require(req.data, "digest", bool)
        limit = require(
            req.data,
            "limit",
        )

        if limit == -1:
            begin = 0
        else:
            begin = now() - limit

        dev = req.user

        # here we do not strictly limit the role to issue
        # if relation.role != Role.DEV:
        #     return STATUS(1)

        merges = MergeRequest.objects.filter(
            user_authored=dev,
            authoredAt__gte=begin,
            repo__project=req.auth["proj"],
        )
        commits = Commit.objects.filter(
            user_committer=dev,
            createdAt__gte=begin,
            repo__project=req.auth["proj"],
        )
        issues = Issue.objects.filter(
            user_assignee=dev,
            closedAt__gte=begin,
            repo__project=req.auth["proj"],
        )

        if digest:
            additions = sum([c.additions for c in commits])
            deletions = sum([c.deletions for c in commits])
            res = {
                "mr_count": len(merges),
                "commit_count": len(commits),
                "additions": additions,
                "deletions": deletions,
                "issue_count": len(issues),
                "issue_times": [round(i.closedAt - i.authoredAt) for i in issues],
                "commit_times": [round(c.createdAt) for c in commits],
            }
            return Response({"code": 0, "data": res})
        else:
            res = {
                "merges": [
                    {
                        **model_to_dict(m, fields=["id", "merge_id", "title", "url"]),
                        "repo": m.repo.title,
                    }
                    for m in merges
                ],
                "commits": [
                    {
                        **model_to_dict(
                            c,
                            fields=[
                                "id",
                                "hash_id",
                                "message",
                                "createdAt",
                                "url",
                                "additions",
                                "deletions",
                            ],
                        ),
                        "repo": c.repo.title,
                    }
                    for c in commits
                ],
                "issues": [
                    {
                        **model_to_dict(
                            i,
                            fields=[
                                "id",
                                "issue_id",
                                "title",
                                "authoredAt",
                                "closedAt",
                                "url",
                            ],
                        ),
                        "repo": i.repo.title,
                    }
                    for i in issues
                ],
            }
            return Response({"code": 0, "data": res})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def forward_tree(self, req: Request):
        repo = require(req.query_params, "repo", int)
        path = req.query_params.get("path", None)
        ref = require(req.query_params, "ref", str)

        r = RemoteRepo.objects.filter(
            repo__disabled=False, repo__id=repo, repo__project=req.auth["proj"]
        ).first()
        if not r:
            return STATUS(1)

        if r.type not in type_map:
            return STATUS(2)

        fetcher = type_map[r.type](
            json.loads(r.info)["base_url"], r.remote_id, r.access_token
        )

        @func_set_timeout(3)
        def request_to_tree():
            return fetcher.tree(ref, path)

        try:
            code, body = request_to_tree()
        except FunctionTimedOut:
            return STATUS(4)
        except:
            return STATUS(5)

        return Response({"code": 0, "data": {"http_status": code, "body": body}})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def forward_branches(self, req: Request):
        repo = require(req.query_params, "repo", int)

        r = RemoteRepo.objects.filter(
            repo__disabled=False, repo__id=repo, repo__project=req.auth["proj"]
        ).first()
        if not r:
            return STATUS(1)

        if r.type not in type_map:
            return STATUS(2)

        fetcher = type_map[r.type](
            json.loads(r.info)["base_url"], r.remote_id, r.access_token
        )

        @func_set_timeout(3)
        def request_to_branches():
            return fetcher.branches()

        try:
            code, body = request_to_branches()
        except FunctionTimedOut:
            return STATUS(4)
        except:
            return STATUS(5)

        return Response({"code": 0, "data": {"http_status": code, "body": body}})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def forward_code_sr(self, req: Request):
        path = require(req.query_params, "path", str)
        ref = require(req.query_params, "ref", str)
        repo = require(req.query_params, "repo", int)

        r = RemoteRepo.objects.filter(
            repo__disabled=False, repo__id=repo, repo__project=req.auth["proj"]
        ).first()
        if not r:
            return STATUS(1)

        if r.type not in type_map:
            return STATUS(2)

        fetcher = type_map[r.type](
            json.loads(r.info)["base_url"], r.remote_id, r.access_token
        )

        @func_set_timeout(2)
        def request_to_blame():
            return fetcher.blame(path, ref)

        try:
            code, body = request_to_blame()
        except FunctionTimedOut:
            return STATUS(4)
        except:
            return STATUS(5)

        if code != 200:
            return Response({"code": 3, "data": {"code": code}})

        resp = []
        SRs = {}
        Commits = {}

        for relation in body:
            remote_commit = relation["commit"]
            lines = relation["lines"]
            local_commit = Commit.objects.filter(
                repo__project=req.auth["proj"],
                hash_id=remote_commit["id"],
                repo__id=repo,
            ).first()
            sr = None
            if local_commit:
                sr = CommitSRAssociation.objects.filter(commit=local_commit).first()
                if sr:
                    sr = sr.SR
                    SRs[sr.id] = model_to_dict(sr, exclude=["IR"])
                Commits[local_commit.hash_id] = model_to_dict(
                    local_commit, exclude=["disabled"]
                )
            resp += [
                {
                    "local_commit": local_commit.id if local_commit else None,
                    "remote_commit": None if local_commit else remote_commit,
                    "lines": lines,
                    "SR": sr.id if sr else None,
                }
            ]

        return Response(
            {"code": 0, "data": {"relationship": resp, "SR": SRs, "Commits": Commits}}
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_commits(self, req: Request):
        from_num = require(req.query_params, "from", int)
        size = require(req.query_params, "size", int)

        if size > 100:
            size = 100
        commits = (
            Commit.objects.filter(
                repo__project=req.auth["proj"], repo__disabled=False, disabled=False
            )
            .order_by("-createdAt")
            .values(
                "id",
                "hash_id",
                "repo",
                "title",
                "commiter_email",
                "commiter_name",
                "createdAt",
                "user_committer",
                "additions",
                "deletions",
            )[from_num : size + from_num]
        )
        return Response(
            {
                "code": 0,
                "data": {
                    "payload": commits,
                    "total_size": Commit.objects.filter(
                        repo__project=req.auth["proj"],
                        repo__disabled=False,
                        disabled=False,
                    ).count(),
                    "from": from_num,
                    "data_size": size,
                    "related_set": None,
                },
            }
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_bugs(self, req: Request):
        from_num = require(req.query_params, "from", int)
        size = require(req.query_params, "size", int)
        return Response(
            pagination(
                Issue.objects.filter(
                    repo__project=req.auth["proj"],
                    repo__disabled=False,
                    disabled=False,
                    is_bug=True,
                ),
                from_num,
                size,
                order="-authoredAt",
            )
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_merges(self, req: Request):
        from_num = require(req.query_params, "from", int)
        size = require(req.query_params, "size", int)
        return Response(
            pagination(
                MergeRequest.objects.filter(
                    repo__project=req.auth["proj"], repo__disabled=False, disabled=False
                ),
                from_num,
                size,
                order="-authoredAt",
            )
        )

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_single_commit(self, req: Request):
        commit_id = require(req.query_params, "id", int)
        commit = Commit.objects.filter(
            repo__project=req.auth["proj"], repo__disabled=False, id=commit_id
        ).first()
        if not commit:
            return FAIL

        return Response({"code": 0, "data": model_to_dict(commit)})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_single_bug(self, req: Request):
        bug_id = require(req.query_params, "id", int)
        bug = Issue.objects.filter(
            repo__project=req.auth["proj"], repo__disabled=False, id=bug_id, is_bug=True
        ).first()
        if not bug:
            return FAIL

        return Response({"code": 0, "data": model_to_dict(bug)})

    @project_rights("AnyMember")
    @action(detail=False, methods=["GET"])
    def project_single_merge(self, req: Request):
        merge_id = require(req.query_params, "id", int)
        merge = MergeRequest.objects.filter(
            repo__project=req.auth["proj"], repo__disabled=False, id=merge_id
        ).first()
        if not merge:
            return FAIL

        return Response({"code": 0, "data": model_to_dict(merge)})

    @project_rights("AnyMember")
    @action(detail=False, methods=["POST"])
    def search_merge(self, req: Request):
        title_only = require(req.data, "title_only", bool)
        kw = require(req.data, "kw", str)
        limit = require(req.data, "limit", int)
        vals = ("id", "merge_id", "repo", "title", "description", "state", "authoredAt")
        if title_only:
            res = (
                MergeRequest.objects.filter(
                    repo__project=req.auth["proj"], repo__disabled=False, disabled=False
                )
                .filter(title__contains=kw)
                .order_by("-authoredAt")
                .values(*vals)[:limit]
            )
        else:
            res = (
                MergeRequest.objects.filter(
                    repo__project=req.auth["proj"], repo__disabled=False, disabled=False
                )
                .filter(Q(title__contains=kw) | Q(description__contains=kw))
                .order_by("-authoredAt")
                .values(*vals)[:limit]
            )

        return Response(
            {
                "code": 0,
                "data": res,
            }
        )

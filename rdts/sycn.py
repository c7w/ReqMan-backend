import pytz
from backend.settings import TIME_ZONE
from time import sleep
import json
from iso8601 import parse_date
from utils.common import extract_sr_pattern, extract_issue_pattern
from django.forms.models import model_to_dict
from rms.models import *
from ums.models import *
from rdts.models import *

SMALL_INTERVAL = 0
BIG_INTERVAL = 0.5
DIFF_LIMIT = 7 * 24 * 3600


def update_obj(model, dic):
    for k, v in dic.items():
        setattr(model, k, v)
    model.save()


def now():
    return dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))


def search_for_commit_update(commits, r: RemoteRepo, ori_commits, req, crawl=None):
    def update_sr_commit(comm: Commit, title):
        if CommitSRAssociation.objects.filter(commit=comm, auto_added=False).first():
            return
        pattern = extract_sr_pattern(title, r.repo.project)
        print(title, pattern)
        if pattern:
            sr = SR.objects.filter(
                title=pattern, project=r.repo.project, disabled=False
            ).first()
            CommitSRAssociation.objects.filter(commit=comm, auto_added=True).delete()
            if sr:
                CommitSRAssociation.objects.create(commit=comm, SR=sr, auto_added=True)

    def update_user_commit(c: Commit):
        _rec = UserMinorEmailAssociation.objects.filter(
            email=c.commiter_email,  # verified=True
        ).first()

        if _rec:
            c.user_committer = _rec.user
        else:
            c.user_committer = None
        c.save()

    def append_diff(_kw: dict):
        diff_status, additions, deletions, diffs = req.commit_diff_lines(c["id"])
        print("diff status", diff_status, additions, deletions)
        _kw["additions"] = additions
        _kw["deletions"] = deletions
        _kw["diff"] = json.dumps(diffs, ensure_ascii=False)
        return _kw

    updated = False
    for c in commits:
        kw = {
            "hash_id": c["id"],
            "repo": r.repo,
            "title": c["title"],
            "message": c["message"],
            "commiter_email": c["committer_email"],
            "commiter_name": c["committer_name"],
            "createdAt": dt.datetime.timestamp(parse_date(c["created_at"])),
            "url": c["web_url"],
        }
        cs = ori_commits.filter(hash_id=c["id"])
        if len(cs):
            oc: Commit = cs.first()
            old_key = {
                "hash_id": oc.hash_id,
                "repo": oc.repo,
                "title": oc.title,
                "message": oc.message,
                "commiter_email": oc.commiter_email,
                "commiter_name": oc.commiter_name,
                "createdAt": oc.createdAt,
                "url": oc.url,
            }
            if old_key != kw:
                updated = True
                kw = append_diff(kw)
                update_obj(oc, kw)
                if crawl:
                    CommitCrawlAssociation.objects.create(
                        commit=oc, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
            update_sr_commit(oc, kw["title"])
            update_user_commit(oc)
        else:
            updated = True
            kw = append_diff(kw)
            print("create", kw["additions"], kw["deletions"], kw["commiter_email"])
            new_c = Commit.objects.create(**kw)
            if crawl:
                CommitCrawlAssociation.objects.create(
                    commit=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
            update_sr_commit(new_c, kw["title"])
            update_user_commit(new_c)
    return updated


def search_for_issue_update(issues, r: RemoteRepo, ori_issues, crawl=None):
    def update_sr_issue(iss: Issue, title):
        if IssueSRAssociation.objects.filter(issue=iss, auto_added=False).first():
            return
        pattern = extract_sr_pattern(title, r.repo.project)
        print(pattern)
        if pattern:
            sr = SR.objects.filter(
                title=pattern, project=r.repo.project, disabled=False
            ).first()
            IssueSRAssociation.objects.filter(issue=iss, auto_added=True).delete()
            if sr:
                IssueSRAssociation.objects.create(issue=iss, SR=sr, auto_added=True)

    def update_user_issue(iss: Issue):
        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=iss.assigneeUserName
        ).first()
        if _rec:
            iss.user_assignee = _rec.user
        else:
            iss.user_assignee = None

        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=iss.authoredByUserName
        ).first()
        if _rec:
            iss.user_authored = _rec.user
        else:
            iss.user_authored = None

        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=iss.closedByUserName
        ).first()

        if _rec:
            iss.user_closed = _rec.user
        else:
            iss.user_closed = None

        iss.save()

    updated = False
    for c in issues:
        kw = {
            "issue_id": c["iid"],
            "repo": r.repo,
            "title": c["title"],
            "description": c["description"],
            "state": c["state"],
            "authoredByUserName": c["author"]["username"],
            "authoredAt": dt.datetime.timestamp(parse_date(c["created_at"])),
            "updatedAt": dt.datetime.timestamp(parse_date(c["updated_at"])),
            "closedByUserName": c["closed_by"]["username"]
            if c["closed_by"] is not None
            else "",
            "closedAt": dt.datetime.timestamp(parse_date(c["closed_at"]))
            if c["closed_at"] is not None
            else None,
            "assigneeUserName": c["assignee"]["username"]
            if c["assignee"] is not None
            else "",
            "url": c["web_url"],
            "labels": json.dumps(c["labels"], ensure_ascii=False),
            "is_bug": "bug" in c["labels"],
        }
        iss = ori_issues.filter(issue_id=c["iid"])
        if len(iss):
            m: Issue = iss.first()
            prev_info = {
                "issue_id": m.issue_id,
                "repo": m.repo,
                "title": m.title,
                "description": m.description,
                "state": m.state,
                "authoredByUserName": m.authoredByUserName,
                "authoredAt": m.authoredAt,
                "updatedAt": m.updatedAt,
                "closedByUserName": m.closedByUserName,
                "closedAt": m.closedAt,
                "assigneeUserName": m.assigneeUserName,
                "url": m.url,
                "labels": m.labels,
                "is_bug": m.is_bug,
            }
            if prev_info != kw:
                updated = True
                update_obj(m, kw)
                if crawl:
                    IssueCrawlAssociation.objects.create(
                        issue=m, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
            update_sr_issue(m, kw["title"])
            update_user_issue(m)
        else:
            updated = True
            new_c = Issue.objects.create(**kw)
            if crawl:
                IssueCrawlAssociation.objects.create(
                    issue=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
            update_sr_issue(new_c, kw["title"])
            update_user_issue(new_c)
    return updated


def search_for_mr_addition(
    merges,
    r: RemoteRepo,
    ori_merges,
    crawl=None,
):
    updated = False

    def update_sr_merge(_mr: MergeRequest, title):
        if MRSRAssociation.objects.filter(MR=_mr, auto_added=False).first():
            return
        pattern = extract_sr_pattern(title, r.repo.project)
        print(pattern)
        if pattern:
            sr = SR.objects.filter(
                title=pattern, project=r.repo.project, disabled=False
            ).first()
            MRSRAssociation.objects.filter(MR=_mr, auto_added=True).delete()
            if sr:
                MRSRAssociation.objects.create(MR=_mr, SR=sr, auto_added=True)

    def update_user_merge(_mr: MergeRequest):
        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=_mr.authoredByUserName
        ).first()

        if _rec:
            _mr.user_authored = _rec.user
        else:
            _mr.user_authored = None

        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=_mr.reviewedByUserName
        ).first()

        if _rec:
            _mr.user_reviewed = _rec.user
        else:
            _mr.user_reviewed = None

        _mr.save()

    def update_merge_issue(_mr: MergeRequest):
        if IssueMRAssociation.objects.filter(
            MR=_mr, auto_added=False
        ).first():  # manual top priority
            return
        issue_str = extract_issue_pattern(_mr.title, r.repo.project)
        if issue_str:
            issue_id = int(issue_str)
            issue = Issue.objects.filter(issue_id=issue_id).first()
            IssueMRAssociation.objects.filter(MR=_mr, auto_added=True).delete()
            print("pattern", issue_id, "issue", issue)
            if issue:
                IssueMRAssociation.objects.create(issue=issue, MR=_mr, auto_added=True)

    print(str(len(merges)))
    for c in merges:
        kw = {
            "merge_id": c["iid"],
            "repo": r.repo,
            "title": c["title"],
            "description": c["description"],
            "state": c["state"],
            "authoredByUserName": c["author"]["username"],
            "authoredAt": dt.datetime.timestamp(parse_date(c["created_at"])),
            "reviewedByUserName": c["merged_by"]["username"]
            if c["merged_by"] is not None
            else "",
            "reviewedAt": dt.datetime.timestamp(parse_date(c["merged_at"]))
            if c["merged_at"] is not None
            else None,
            "url": c["web_url"],
        }
        mr = ori_merges.filter(merge_id=c["iid"])
        if len(mr):
            m: MergeRequest = mr.first()
            prev_info = {
                "merge_id": m.merge_id,
                "repo": m.repo,
                "title": m.title,
                "description": m.description,
                "state": m.state,
                "authoredByUserName": m.authoredByUserName,
                "authoredAt": m.authoredAt,
                "reviewedByUserName": m.reviewedByUserName,
                "reviewedAt": m.reviewedAt,
                "url": m.url,
            }
            if prev_info != kw:
                updated = True
                update_obj(m, kw)
                if crawl:
                    MergeCrawlAssociation.objects.create(
                        merge=m, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
            update_sr_merge(m, kw["title"])
            update_user_merge(m)
            update_merge_issue(m)
        else:
            updated = True
            new_c = MergeRequest.objects.create(**kw)
            if crawl:
                MergeCrawlAssociation.objects.create(
                    merge=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
            update_sr_merge(new_c, kw["title"])
            update_user_merge(new_c)
            update_merge_issue(new_c)
    return updated


def batch_refresh_sr_status(iss_c, mr_c, comm_c, r):

    MR = MergeCrawlAssociation.objects.filter(
        crawl=mr_c, operation__in=["update", "insert"]
    ).order_by("merge__authoredAt")
    CM = CommitCrawlAssociation.objects.filter(
        crawl=comm_c, operation__in=["update", "insert"]
    ).order_by("commit__createdAt")
    IS = IssueCrawlAssociation.objects.filter(
        crawl=iss_c, operation__in=["update", "insert"]
    ).order_by("issue__authoredAt")

    print(MR, CM, IS, iss_c, mr_c, comm_c)

    for c in CM:
        relation = CommitSRAssociation.objects.filter(commit=c.commit).first()
        if relation:
            print(relation.SR.state)

        if (
            relation
            and relation.SR.state != SR.SRState.WIP
            and relation.SR.state != SR.SRState.Reviewing
            and relation.SR.state != SR.SRState.Done
        ):
            SR_Changelog.objects.create(
                project=r.repo.project,
                SR=relation.SR,
                formerState=relation.SR.state,
                formerDescription=relation.SR.description,
                changedAt=c.commit.createdAt,
                autoAdded=True,
                autoAddCrawl=comm_c,
                autoAddedTriggerType="commit",
                autoAddedTriggerValue=c.commit.id,
            )
            relation.SR.state = SR.SRState.WIP
            relation.SR.save()

    for mr in MR:
        relation = MRSRAssociation.objects.filter(MR=mr.merge).first()

        if relation:
            print(relation.SR.state)
        if (
            relation
            and relation.SR.state != SR.SRState.Done
            and relation.SR.state != SR.SRState.Reviewing
        ):
            SR_Changelog.objects.create(
                project=r.repo.project,
                SR=relation.SR,
                formerState=relation.SR.state,
                formerDescription=relation.SR.description,
                changedAt=mr.merge.authoredAt,
                autoAdded=True,
                autoAddCrawl=mr_c,
                autoAddedTriggerType="merge",
                autoAddedTriggerValue=mr.merge.id,
            )
            relation.SR.state = SR.SRState.Reviewing
            relation.SR.save()

    for issue in IS:
        if issue.issue.closedAt:
            relation = IssueSRAssociation.objects.filter(issue=issue.issue).first()
            if relation:
                print(relation.SR.state)
            if relation and relation.SR.state != SR.SRState.Done:
                SR_Changelog.objects.create(
                    project=r.repo.project,
                    SR=relation.SR,
                    formerState=relation.SR.state,
                    formerDescription=relation.SR.description,
                    changedAt=issue.issue.closedAt,
                    autoAdded=True,
                    autoAddCrawl=iss_c,
                    autoAddedTriggerType="issue",
                    autoAddedTriggerValue=issue.issue.id,
                )
                relation.SR.state = SR.SRState.Done
                relation.SR.save()

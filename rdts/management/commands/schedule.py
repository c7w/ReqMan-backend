from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.blocking import BlockingScheduler
from rdts.models import *
from rms.models import *
from ums.models import UserRemoteUsernameAssociation, UserMinorEmailAssociation
from rdts.query_class import type_map, Gitlab
import datetime as dt
import pytz
from backend.settings import TIME_ZONE
from time import sleep
import json
from iso8601 import parse_date

from utils.common import extract_sr_pattern

SMALL_INTERVAL = 0.5
BIG_INTERVAL = 1
DIFF_LIMIT = 7 * 24 * 3600


def update_obj(model, dic):
    for k, v in dic.items():
        setattr(model, k, v)
    model.save()


def now():
    return dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))


class Command(BaseCommand):
    help = "Run Schedule Tasks"

    def get_merge(self, r: RemoteRepo, req):
        def update_sr_merge(mr: MergeRequest, title):
            pattern = extract_sr_pattern(title)
            print(pattern)
            if pattern:
                sr = SR.objects.filter(pattern=pattern, project=r.repo.project).first()
                MRSRAssociation.objects.filter(MR=mr).delete()
                if sr:
                    MRSRAssociation.objects.create(MR=mr, SR=sr)

        def update_user_merge(mr: MergeRequest):
            _rec = UserRemoteUsernameAssociation.objects.filter(
                repository=r.repo, remote_name=mr.authoredByUserName
            ).first()

            if _rec:
                mr.user_authored = _rec.user

            _rec = UserRemoteUsernameAssociation.objects.filter(
                repository=r.repo, remote_name=mr.reviewedByUserName
            ).first()

            if _rec:
                mr.user_reviewed = _rec.user

            mr.save()

        self.stdout.write("begin query merges")
        # make requests
        merges = []
        i = 1
        while True:
            sleep(SMALL_INTERVAL)
            self.stdout.write(f" Begin merges on page {i}")
            part = req.merges(i)
            if part[0] == 200:
                if len(part[1]):
                    merges += part[1]
                    i += 1
                else:
                    break
            else:
                CrawlLog.objects.create(
                    repo=r,
                    time=now(),
                    request_type="merge",
                    status=part[0],
                    message=part[1]["message"],
                )
                return
        self.stdout.write(str(len(merges)))

        # process merges
        crawl = CrawlLog.objects.create(repo=r, time=now(), request_type="merge")
        merges_dic = {}

        # hash merges
        for c in merges:
            merges_dic[c["iid"]] = c

        ori_merges = MergeRequest.objects.filter(repo=r.repo, disabled=False)

        updated = False

        # search for deletion
        for c in ori_merges:
            if c.merge_id not in merges_dic:
                updated = True
                c.disabled = True
                c.save()
                MergeCrawlAssociation.objects.create(
                    merge=c, crawl=crawl, operation=CrawlerOp.REMOVE
                )
                MRSRAssociation.objects.filter(MR=c).delete()

        # search for addition
        self.stdout.write(str(len(merges)))
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
                    MergeCrawlAssociation.objects.create(
                        merge=m, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
                update_sr_merge(m, kw["title"])
                update_user_merge(m)
            else:
                updated = True
                new_c = MergeRequest.objects.create(**kw)
                MergeCrawlAssociation.objects.create(
                    merge=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
                update_sr_merge(new_c, kw["title"])
                update_user_merge(new_c)

        crawl.finished = True
        crawl.updated = updated
        crawl.save()

    def get_commit(self, r: RemoteRepo, req):
        def update_sr_commit(comm: Commit, title):
            pattern = extract_sr_pattern(title)
            print(pattern)
            if pattern:
                sr = SR.objects.filter(pattern=pattern, project=r.repo.project).first()
                CommitSRAssociation.objects.filter(commit=comm).delete()
                if sr:
                    CommitSRAssociation.objects.create(commit=comm, SR=sr)

        def update_user_commit(c: Commit):
            _rec = UserMinorEmailAssociation.objects.filter(
                email=c.commiter_email, verified=True
            ).first()

            if _rec:
                c.user_committer = _rec.user
            c.save()

        def append_diff(_kw: dict):
            diff_status, additions, deletions, diffs = req.commit_diff_lines(c["id"])
            # print("diff status", diff_status, additions, deletions)
            _kw["additions"] = additions
            _kw["deletions"] = deletions
            _kw["diff"] = json.dumps(diffs, ensure_ascii=False)
            return _kw

        self.stdout.write("begin query commits")
        # make requests
        commits = []
        i = 1
        while True:
            # sleep(SMALL_INTERVAL)
            self.stdout.write(f" Begin commits on page {i}")
            part = req.commits(i)
            if part[0] == 200:
                if len(part[1]):
                    commits += part[1]
                    i += 1
                else:
                    break
            else:
                CrawlLog.objects.create(
                    repo=r,
                    time=now(),
                    request_type="commit",
                    status=part[0],
                    message=part[1]["message"],
                )
                return
        self.stdout.write(str(len(commits)))

        # process commits
        crawl = CrawlLog.objects.create(repo=r, time=now(), request_type="commit")
        commits_dic = {}

        # hash commits
        for c in commits:
            commits_dic[c["id"]] = c

        ori_commits = Commit.objects.filter(repo=r.repo, disabled=False)

        updated = False

        # search for deletion
        for c in ori_commits:
            if c.hash_id not in commits_dic:
                updated = True
                c.disabled = True
                c.save()
                CommitCrawlAssociation.objects.create(
                    commit=c, crawl=crawl, operation=CrawlerOp.REMOVE
                )
                CommitSRAssociation.objects.filter(commit=c).delete()

        # search for addition
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
                    CommitCrawlAssociation.objects.create(
                        commit=oc, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
                update_sr_commit(oc, kw["title"])
                update_user_commit(oc)
            else:
                updated = True
                kw = append_diff(kw)
                print("create", kw["additions"], kw["commiter_email"])
                new_c = Commit.objects.create(**kw)
                CommitCrawlAssociation.objects.create(
                    commit=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
                update_sr_commit(new_c, kw["title"])
                update_user_commit(new_c)
        crawl.finished = True
        crawl.updated = updated
        crawl.save()

    def get_issue(self, r: RemoteRepo, req):
        def update_sr_issue(iss: Issue, title):
            pattern = extract_sr_pattern(title)
            print(pattern)
            if pattern:
                sr = SR.objects.filter(pattern=pattern, project=r.repo.project).first()
                IssueSRAssociation.objects.filter(issue=iss).delete()
                if sr:
                    IssueSRAssociation.objects.create(issue=iss, SR=sr)

        def update_user_issue(iss: Issue):
            _rec = UserRemoteUsernameAssociation.objects.filter(
                repository=r.repo, remote_name=iss.assigneeUserName
            ).first()
            if _rec:
                iss.user_assignee = _rec.user

            _rec = UserRemoteUsernameAssociation.objects.filter(
                repository=r.repo, remote_name=iss.authoredByUserName
            ).first()
            if _rec:
                iss.user_authored = _rec.user

            _rec = UserRemoteUsernameAssociation.objects.filter(
                repository=r.repo, remote_name=iss.closedByUserName
            ).first()

            if _rec:
                iss.user_closed = _rec.user

            iss.save()

        self.stdout.write("begin query issues")
        # make requests
        issues = []
        i = 1
        while True:
            sleep(SMALL_INTERVAL)
            self.stdout.write(f" Begin issues on page {i}")
            part = req.issues(i)
            if part[0] == 200:
                if len(part[1]):
                    issues += part[1]
                    i += 1
                else:
                    break
            else:
                CrawlLog.objects.create(
                    repo=r,
                    time=now(),
                    request_type="issue",
                    status=part[0],
                    message=part[1]["message"],
                )
                return
        self.stdout.write(str(len(issues)))

        # process issues
        crawl = CrawlLog.objects.create(repo=r, time=now(), request_type="issue")
        issues_dic = {}

        # hash issues
        for c in issues:
            issues_dic[c["iid"]] = c

        ori_issues = Issue.objects.filter(repo=r.repo, disabled=False)

        updated = False

        # search for deletion
        for c in ori_issues:
            if c.issue_id not in issues_dic:
                updated = True
                c.disabled = True
                c.save()
                IssueCrawlAssociation.objects.create(
                    issue=c, crawl=crawl, operation=CrawlerOp.REMOVE
                )
                IssueSRAssociation.objects.filter(issue=c).delete()

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
                    IssueCrawlAssociation.objects.create(
                        issue=m, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
                update_sr_issue(m, kw["title"])
                update_user_issue(m)
            else:
                updated = True
                new_c = Issue.objects.create(**kw)
                IssueCrawlAssociation.objects.create(
                    issue=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )
                update_sr_issue(new_c, kw["title"])
                update_user_issue(new_c)

        crawl.finished = True
        crawl.updated = updated
        crawl.save()

    def crawl_all(self):
        remote_repos = RemoteRepo.objects.filter(
            enable_crawling=True, repo__disabled=False
        )
        self.stdout.write("Repos: " + ", ".join([str(r.id) for r in remote_repos]))

        for r in remote_repos:
            if r.type not in type_map:
                CrawlLog.objects.create(
                    repo=r, time=now(), status=-1, message="Repo type not supported"
                )
                continue
            req = type_map[r.type](
                json.loads(r.info)["base_url"], r.remote_id, r.access_token
            )

            self.get_issue(r, req)
            sleep(BIG_INTERVAL)
            self.get_commit(r, req)
            sleep(BIG_INTERVAL)
            self.get_merge(r, req)
            sleep(BIG_INTERVAL)

        self.stdout.write("END OF TASK CRAWL")

    def handle(self, *args, **options):
        s = BlockingScheduler()
        self.stdout.write("Scheduler Initialized")
        s.add_job(self.crawl_all, "interval", minutes=5)
        s.start()
        # self.crawl_all()

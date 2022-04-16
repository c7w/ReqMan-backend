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
from utils.common import extract_sr_pattern, extract_issue_pattern
from django.forms.models import model_to_dict
from rdts.sycn import *

SMALL_INTERVAL = 0
BIG_INTERVAL = 0.5
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
        # for c in ori_merges:
        #     if c.merge_id not in merges_dic:
        #         updated = True
        #         c.disabled = True
        #         c.save()
        #         MergeCrawlAssociation.objects.create(
        #             merge=c, crawl=crawl, operation=CrawlerOp.REMOVE
        #         )
        #         MRSRAssociation.objects.filter(MR=c).delete()

        # search for addition
        add_updated = search_for_mr_addition(merges, r, ori_merges, crawl)
        if not updated:
            updated = add_updated

        crawl.finished = True
        crawl.updated = updated
        crawl.save()
        return crawl

    def get_commit(self, r: RemoteRepo, req):
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
        # for c in ori_commits:
        #     if c.hash_id not in commits_dic:
        #         updated = True
        #         c.disabled = True
        #         c.save()
        #         CommitCrawlAssociation.objects.create(
        #             commit=c, crawl=crawl, operation=CrawlerOp.REMOVE
        #         )
        #         CommitSRAssociation.objects.filter(commit=c).delete()

        # search for addition
        add_upd = search_for_commit_update(commits, r, ori_commits, req, crawl)
        if add_upd:
            updated = True

        crawl.finished = True
        crawl.updated = updated
        crawl.save()
        return crawl

    def get_issue(self, r: RemoteRepo, req):
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
        # for c in ori_issues:
        #     if c.issue_id not in issues_dic:
        #         updated = True
        #         c.disabled = True
        #         c.save()
        #         IssueCrawlAssociation.objects.create(
        #             issue=c, crawl=crawl, operation=CrawlerOp.REMOVE
        #         )
        #         IssueSRAssociation.objects.filter(issue=c).delete()

        # search for addition
        add_update = search_for_issue_update(issues, r, ori_issues, crawl)
        if add_update:
            updated = add_update

        crawl.finished = True
        crawl.updated = updated
        crawl.save()
        return crawl

    def crawl_all(self):
        remote_repos = list(
            RemoteRepo.objects.filter(enable_crawling=True, repo__disabled=False)
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

            iss_c = self.get_issue(r, req)
            sleep(BIG_INTERVAL)
            mr_c = self.get_merge(r, req)
            sleep(BIG_INTERVAL)
            comm_c = self.get_commit(r, req)
            sleep(BIG_INTERVAL)

            batch_refresh_sr_status(iss_c, mr_c, comm_c, r)

        self.stdout.write("END OF TASK CRAWL")

    def handle(self, *args, **options):
        s = BlockingScheduler()
        self.stdout.write("Scheduler Initialized")
        s.add_job(self.crawl_all, "interval", minutes=5)
        s.start()
        # self.crawl_all()

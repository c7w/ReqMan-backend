from django.core.management.base import BaseCommand, CommandError
from apscheduler.schedulers.blocking import BlockingScheduler
from rdts.models import *
from rdts.query_class import type_map, Gitlab
import datetime as dt
import pytz
from backend.settings import TIME_ZONE
from time import sleep
import json
from iso8601 import parse_date


def test_job():
    print(123)


def now():
    return dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))


class Command(BaseCommand):
    help = "Run Schedule Tasks"

    def crawl_all(self):
        for r in RemoteRepo.objects.filter(enable_crawling=True):
            if r.type not in type_map:
                CrawlLog.objects.create(
                    repo=r, time=now(), status=-1, message="Repo type not supported"
                )
                continue
            req = type_map[r.type](
                json.loads(r.info)["base_url"], r.remote_id, r.access_token
            )

            # make requests
            commits = req.commits()
            sleep(1)
            merges = req.merges()
            sleep(1)
            issues = req.issues()

            # process commits
            if commits[0] == 200:
                crawl = CrawlLog.objects.create(
                    repo=r, time=now(), request_type="commit"
                )
                commits = commits[1].json()
                commits_dic = {}

                # hash commits
                for c in commits:
                    commits_dic[c["id"]] = c

                ori_commits = Commit.objects.filter(repo=r.repo)

                # search for deletion
                for c in ori_commits:
                    if c.hash_id not in commits_dic:
                        c.disabled = True
                        c.save()
                        CommitCrawlAssociation.objects.create(
                            commit=c, crawl=crawl, operation="remove"
                        )

                # search for addition
                for c in commits:
                    if not ori_commits.filter(hash_id=c["id"]).first():
                        Commit.objects.create(
                            hash_id=c["id"],
                            repo=r.repo,
                            title=c["title"],
                            message=c["message"],
                            committer_email=c["committer_email"],
                            committer_name=c["committer_name"],
                            createdAt=dt.datetime.timestamp(
                                parse_date(c["created_at"])
                            ),
                        )

                crawl.finished = True
                crawl.save()

    def handle(self, *args, **options):
        # s = BlockingScheduler()
        # s.add_job(test_job, 'interval', seconds=1)
        # s.start()
        self.crawl_all()

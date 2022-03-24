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

SMALL_INTERVAL = 0.5
BIG_INTERVAL = 1


def now():
    return dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))


class Command(BaseCommand):
    help = "Run Schedule Tasks"

    def get_merge(self, r: RemoteRepo, req):
        print("begin query merges")
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
        print(len(merges))

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

        # search for addition
        print(len(merges))
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
                    "url": c["web_url"],
                }
                if prev_info != kw:
                    updated = True
                    mr.update(**kw)
                    MergeCrawlAssociation.objects.create(
                        merge=m, crawl=crawl, operation=CrawlerOp.UPDATE
                    )
            else:
                updated = True
                new_c = MergeRequest.objects.create(**kw)
                MergeCrawlAssociation.objects.create(
                    merge=new_c, crawl=crawl, operation=CrawlerOp.INSERT
                )

        crawl.finished = True
        crawl.updated = updated
        crawl.save()

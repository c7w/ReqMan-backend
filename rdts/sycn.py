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




def search_for_mr_addition(merges, r: RemoteRepo, ori_merges, crawl = None, ):
    updated = False
    def update_sr_merge(_mr: MergeRequest, title):
        if MRSRAssociation.objects.filter(MR=_mr, auto_added=False).first():
            return
        pattern = extract_sr_pattern(title)
        print(pattern)
        if pattern:
            sr = SR.objects.filter(
                pattern=pattern, project=r.repo.project, disabled=False
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

        _rec = UserRemoteUsernameAssociation.objects.filter(
            url=r.repo.url, remote_name=_mr.reviewedByUserName
        ).first()

        if _rec:
            _mr.user_reviewed = _rec.user

        _mr.save()

    def update_merge_issue(_mr: MergeRequest):
        if IssueMRAssociation.objects.filter(
            MR=_mr, auto_added=False
        ).first():  # manual top priority
            return
        issue_str = extract_issue_pattern(_mr.title)
        if issue_str:
            issue_id = int(issue_str)
            issue = Issue.objects.filter(issue_id=issue_id).first()
            IssueMRAssociation.objects.filter(MR=_mr, auto_added=True).delete()
            print("pattern", issue_id, "issue", issue)
            if issue:
                IssueMRAssociation.objects.create(
                    issue=issue, MR=_mr, auto_added=True
                )
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

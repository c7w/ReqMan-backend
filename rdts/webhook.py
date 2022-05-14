from rdts.models import RemoteRepo, Repository
from rdts.query_class import RemoteRepoFetcher
from rdts.sycn import *


def push_action(repo: RemoteRepo, body: dict, req):
    commits = body["commits"]
    if len(commits):
        commits = [
            {
                "id": c["id"],
                "message": c["message"],
                "title": c["title"],
                "committer_email": c["author"]["email"],
                "committer_name": c["author"]["email"],
                "created_at": c["timestamp"],
                "web_url": c["url"],
            }
            for c in commits
        ]
        comm_c = CrawlLog.objects.create(
            repo=repo,
            time=now(),
            request_type="commit",
            finished=True,
            updated=True,
            is_webhook=True,
        )
        search_for_commit_update(
            commits,
            repo,
            Commit.objects.filter(repo=repo.repo, disabled=False),
            req,
            comm_c,
        )
        batch_refresh_sr_status(None, None, comm_c, repo)
    else:
        if body["before"].replace("0", "") and body["after"].replace("0", ""):
            return  # no force supported


def mr_action(repo: RemoteRepo, body: dict, req):
    mid = body["object_attributes"]["iid"]
    status, bdy = req.single_merge(mid)
    if status != 200:
        print(status, bdy)
        return
    bdy["updated_at"] = now()
    mr_c = CrawlLog.objects.create(
        repo=repo,
        time=now(),
        request_type="merge",
        finished=True,
        updated=True,
        is_webhook=True,
    )
    search_for_mr_addition(
        [bdy], repo, MergeRequest.objects.filter(repo=repo.repo, disabled=False), mr_c
    )
    batch_refresh_sr_status(None, mr_c, None, repo)


def issue_action(repo: RemoteRepo, body: dict, req: RemoteRepoFetcher):
    iid = body["object_attributes"]["iid"]
    status, bdy = req.single_issue(iid)
    if status != 200:
        print(status, bdy)
        return
    bdy["updated_at"] = now()
    iss_c = CrawlLog.objects.create(
        repo=repo,
        time=now(),
        request_type="issue",
        finished=True,
        updated=True,
        is_webhook=True,
    )
    search_for_issue_update(
        [bdy], repo, Issue.objects.filter(repo=repo.repo, disabled=False), iss_c
    )
    batch_refresh_sr_status(iss_c, None, None, repo)

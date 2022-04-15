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
                "title": c["message"],
                "committer_email": c["author"]["email"],
                "committer_name": c["author"]["email"],
                "created_at": c["timestamp"],
                "web_url": c["url"],
            }
            for c in commits
        ]
        search_for_commit_update(
            commits, repo, Commit.objects.filter(repo=repo.repo, disabled=False), req
        )
    else:
        if body["before"].replace("0", "") and body["after"].replace("0", ""):
            return  # no force supported


def mr_action(repo: RemoteRepo, body: dict, req):
    mid = body["object_attributes"]["iid"]
    status, bdy = req.single_merge(mid)
    if status != 200:
        print(status, bdy)
        return
    search_for_mr_addition(
        [bdy], repo, MergeRequest.objects.filter(repo=repo.repo, disabled=False)
    )


def issue_action(repo: RemoteRepo, body: dict, req: RemoteRepoFetcher):
    iid = body["object_attributes"]["iid"]
    status, bdy = req.single_issue(iid)
    if status != 200:
        print(status, bdy)
        return
    search_for_issue_update(
        [bdy], repo, Issue.objects.filter(repo=repo.repo, disabled=False)
    )

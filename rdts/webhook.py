from rdts.models import RemoteRepo, Repository
from rdts.query_class import RemoteRepoFetcher


def push_action(repo: RemoteRepo, body: dict, req):
    pass


def mr_action(repo: RemoteRepo, body: dict, req):
    pass


def issue_action(repo: RemoteRepo, body: dict, req: RemoteRepoFetcher):
    iid = body['object_attributes']['iid']
    status, bdy = req.single_issue(iid)


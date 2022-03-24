from rdts.models import *
from ums.models import *
from rms.models import *

def repoExist(id:int):
    repo = Repository.objects.filter(id=id,disabled=False)
    for r in repo:
        return r

def getRepo(proj:Project):
    return Repository.objects.filter(project=proj,disabled=False)

def getCommit(repo:Repository):
    return Commit.objects.filter(repo=repo,disabled=False)

def getMR(repo:Repository):
    return MergeRequest.objects.filter(repo=repo,disabled=False)

def getIssue(repo:Repository):
    return Issue.objects.filter(repo=repo,disabled=False)

def getCommitSR(repo:Repository):
    commit = getCommit(repo)
    return CommitSRAssociation.objects.filter(commit__in=commit)

def getMRSR(repo:Repository):
    MR = getMR(repo)
    return MRSRAssociation.objects.filter(MR__in = MR)

def getIssueSR(repo:Repository):
    issue = getIssue(repo)
    return IssueSRAssociation.objects.filter(issue__in = issue)
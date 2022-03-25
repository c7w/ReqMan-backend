from rdts.models import *
from rms.utils import judgeTypeFloat, judgeTypeInt, judgeTypeStr
from ums.models import *
from rms.models import *
from ums.utils import require
from utils.exceptions import ParamErr


def repoExist(id: int):
    repo = Repository.objects.filter(id=id, disabled=False)
    for r in repo:
        return r


def getRepo(proj: Project):
    return Repository.objects.filter(project=proj, disabled=False)


def getCommit(repo: Repository):
    return Commit.objects.filter(repo=repo, disabled=False)


def getMR(repo: Repository):
    return MergeRequest.objects.filter(repo=repo, disabled=False)


def getIssue(repo: Repository):
    return Issue.objects.filter(repo=repo, disabled=False)


def getCommitSR(repo: Repository):
    commit = getCommit(repo)
    return CommitSRAssociation.objects.filter(commit__in=commit)


def getMRSR(repo: Repository):
    MR = getMR(repo)
    return MRSRAssociation.objects.filter(MR__in=MR)


def getIssueSR(repo: Repository):
    issue = getIssue(repo)
    return IssueSRAssociation.objects.filter(issue__in=issue)


def createRepo(datas: dict):
    data = {}
    data["url"] = require(datas, "url")
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    data["description"] = require(datas, "description")
    data["createdBy"] = require(datas, "createdBy")
    judgeTypeStr(data["url"])
    judgeTypeStr(data["title"])
    judgeTypeStr(data["description"])
    Repository.objects.create(**data)


def createCommit(datas: dict):
    data = {}
    data["hash_id"] = require(datas, "hash_id")
    data["repo"] = require(datas, "repo")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["message"] = require(datas, "message")
    judgeTypeStr(data["message"])
    data["commiter_email"] = require(datas, "commiter_email")
    judgeTypeStr(data["commiter_email"])
    data["commiter_name"] = require(datas, "commiter_name")
    judgeTypeStr(data["commiter_name"])
    data["createdAt"] = require(datas, "createdAt")
    judgeTypeFloat(data["createdAt"])
    data["url"] = require(datas, "url")
    judgeTypeStr(data["url"])
    Commit.objects.create(**data)


def createMR(datas: dict):
    data = {}
    data["merge_id"] = require(datas, "merge_id")
    judgeTypeInt(data["merge_id"])
    data["repo"] = require(datas, "repo")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["description"] = require(datas, "description")
    judgeTypeStr(data["description"])
    data["state"] = require(datas, "state")
    if not data["state"] in [i for i in MergeRequest.MRState]:
        raise ParamErr(f"wrong type.")
    data["url"] = require(datas, "url")
    judgeTypeStr(data["url"])
    rangeWord = [
        "authoredByEmail",
        "authoredByUserName",
        "authoredAt",
        "reviewedByEmail",
        "reviewedByUserName",
        "reviewedAt",
    ]
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "authoredByEmail" in data:
        judgeTypeStr(data["authoredByEmail"])
    if "authoredByUserName" in data:
        judgeTypeStr(data["authoredByUserName"])
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "reviewedByEmail" in data:
        judgeTypeStr(data["reviewedByEmail"])
    if "reviewedByUserName" in data:
        judgeTypeStr(data["reviewedByUserName"])
    if "reviewedAt" in data:
        judgeTypeFloat(data["reviewedAt"])
    MergeRequest.objects.create(**data)


def createIssue(datas: dict):
    data = {}
    data["issue_id"] = require(datas, "issue_id")
    judgeTypeInt(data["issue_id"])
    data["repo"] = require(datas, "repo")
    data["description"] = require(datas, "description")
    judgeTypeStr(data["description"])
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["url"] = require(datas, "url")
    judgeTypeStr(data["url"])
    data["state"] = require(datas, "state")
    if not data["state"] in [i for i in Issue.IssueState]:
        raise ParamErr(f"wrong type.")
    rangeWord = [
        "authoredByUserName",
        "authoredAt",
        "updateAt",
        "closedByUserName",
        "closedAt",
        "assigneeUserName",
    ]
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "authoredByUserName" in data:
        judgeTypeStr(data["authoredByUserName"])
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "updateAt" in data:
        judgeTypeFloat(data["updateAt"])
    if "closedByUserName" in data:
        judgeTypeStr(data["closedByUserName"])
    if "closedAt" in data:
        judgeTypeFloat(data["closedAt"])
    if "assigneeUserName" in data:
        judgeTypeStr(data["assigneeUserName"])


def createMRSR(datas: dict):
    mr = require(datas, "MRId")
    judgeTypeInt(mr)
    sr = require(datas, "SRId")
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    mr = MergeRequest.objects.filter(id=mr).first()
    if not mr or not sr:
        raise ParamErr(f"wrong MR/SR Id.")
    data = {"MR": mr, "SR": sr}
    MRSRAssociation.objects.create(**data)


def createCommitSR(datas: dict):
    commit = require(datas, "commitId")
    judgeTypeInt(commit)
    sr = require(datas, "SRId")
    commit = Commit.objects.filter(id=commit).first()
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    if not commit or not sr:
        raise ParamErr(f"wrong Commit/SR Id.")
    data = {"commit": commit, "SR": sr}
    CommitSRAssociation.objects.create(**data)


def createIssueSR(datas: dict):
    issue = require(datas, "issueId")
    judgeTypeInt(issue)
    sr = require(datas, "SRId")
    issue = Issue.objects.filter(id=issue).first()
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    if not issue or not sr:
        raise ParamErr(f"wrong Issue/SR Id.")
    data = {"issue": issue, "SR": sr}
    IssueSRAssociation.objects.create(**data)


def createOpertion(proj: Project, type: str, data: dict, user: User):
    dataList = require(data, "data")
    if "repo" in data:
        repoId = data["repo"]
    judgeTypeInt(repoId)
    data = require(dataList, "updateData")
    create = {}
    create.update(data)
    create["project"] = proj
    create["createdBy"] = user
    if repoId > -1:
        repo = Repository.objects.filter(id=repoId).first()
        if not repo:
            raise ParamErr(f"wrong repo Id.")
        create["repo"] = repo
    if type == "repo":
        createRepo(create)
    elif type == "mr":
        createMR(create)
    elif type == "issue":
        createIssue(create)
    elif type == "commit":
        createCommit(create)
    elif type == "mr-sr":
        createMRSR(create)
    elif type == "issue-sr":
        createIssueSR(create)
    elif type == "commit-sr":
        createCommitSR(create)
    return False

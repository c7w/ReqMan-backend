from rdts.models import *
from rms.utils import judgeTypeFloat, judgeTypeInt, judgeTypeStr, judgeStrLen
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


def getIssueMR(issueId: int):
    issue = Issue.objects.filter(id=issueId).first()
    if not issue:
        raise ParamErr(f"Wrong issueId")
    return IssueMRAssociation.objects.filter(issue=issue)


def createRepo(datas: dict):
    data = {}
    data["url"] = require(datas, "url")
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    data["description"] = require(datas, "description")
    data["createdBy"] = require(datas, "createdBy")
    judgeTypeStr(data["url"])
    judgeStrLen(data["url"], 255)
    judgeTypeStr(data["title"])
    judgeStrLen(data["title"], 255)
    judgeTypeStr(data["description"])
    Repository.objects.create(**data)


def createCommit(datas: dict):
    data = {}
    data["hash_id"] = require(datas, "hash_id")
    judgeTypeStr(data["hash_id"])
    judgeStrLen(data["hash_id"], 255)
    data["repo"] = require(datas, "repo")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    judgeStrLen(data["title"], 255)
    data["message"] = require(datas, "message")
    judgeTypeStr(data["message"])
    data["commiter_email"] = require(datas, "commiter_email")
    judgeTypeStr(data["commiter_email"])
    judgeStrLen(data["commiter_email"], 255)
    data["commiter_name"] = require(datas, "commiter_name")
    judgeTypeStr(data["commiter_name"])
    judgeStrLen(data["commiter_name"], 255)
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
    judgeStrLen(data["title"], 255)
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
        judgeStrLen(data["authoredByEmail"], 255)
    if "authoredByUserName" in data:
        judgeTypeStr(data["authoredByUserName"])
        judgeStrLen(data["authoredByUserName"], 255)
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "reviewedByEmail" in data:
        judgeTypeStr(data["reviewedByEmail"])
        judgeStrLen(data["reviewedByEmail"], 255)
    if "reviewedByUserName" in data:
        judgeTypeStr(data["reviewedByUserName"])
        judgeStrLen(data["reviewedByUserName"], 255)
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
    judgeStrLen(data["title"], 255)
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
        judgeStrLen(data["authoredByUserName"], 255)
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "updateAt" in data:
        judgeTypeFloat(data["updateAt"])
    if "closedByUserName" in data:
        judgeTypeStr(data["closedByUserName"])
        judgeStrLen(data["closedByUserName"], 255)
    if "closedAt" in data:
        judgeTypeFloat(data["closedAt"])
    if "assigneeUserName" in data:
        judgeTypeStr(data["assigneeUserName"])
        judgeStrLen(data["assigneeUserName"], 255)
    Issue.objects.create(**data)


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
    exist = MRSRAssociation.objects.filter(MR=mr, SR=sr).first()
    if exist:
        raise ParamErr("Association Exist")
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
    exist = CommitSRAssociation.objects.filter(commit=commit, SR=sr).first()
    if exist:
        raise ParamErr("Association Exist")
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
    exist = IssueSRAssociation.objects.filter(issue=issue, SR=sr).first()
    if exist:
        raise ParamErr("Association Exist")
    IssueSRAssociation.objects.create(**data)


def createIssueMR(datas: dict):
    issue = require(datas, "issueId")
    judgeTypeInt(issue)
    mr = require(datas, "MRId")
    judgeTypeInt(mr)
    issue = Issue.objects.filter(id=issue).first()
    mr = MergeRequest.objects.filter(id=mr).first()
    if not issue or not mr:
        raise ParamErr(f"Wrong issueId or MRId")
    exist = IssueMRAssociation.objects.filter(issue=issue, MR=mr).first()
    if exist:
        raise ParamErr("Association existed.")
    data = {"issue": issue, "MR": mr}
    IssueMRAssociation.objects.create(**data)


def createOpertion(proj: Project, type: str, data: dict, user: User):
    dataList = require(data, "data")
    repoId = -1
    if "repo" in data:
        repoId = data["repo"]
        judgeTypeInt(repoId)
    data = require(dataList, "updateData")
    create = {}
    create.update(data)
    create["createdBy"] = user
    create["project"] = proj
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
    elif type == "issue-mr":
        createIssueMR(create)
    return False


def updateRepo(id: int, datas: dict):
    data = {}
    rangeWord = ["url", "project", "title", "description", "createdBy", "createdAt"]
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "url" in data:
        judgeTypeStr(data["url"])
        judgeStrLen(data["url"], 255)
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
    if "description" in data:
        judgeTypeStr(data["description"])
    if "createdAt" in data:
        judgeTypeFloat(data["createdAt"])
    if "project" in data:
        judgeTypeInt(data["project"])
        project = Project.objects.filter(id=data["project"]).first()
        if not project:
            raise ParamErr(f"wrong project Id.")
        data["project"] = project
    if "createdBy" in data:
        judgeTypeInt(data["createdBy"])
        user = User.objects.filter(id=data["createdBy"]).first()
        if not user:
            raise ParamErr(f"wrong user Id.")
        data["createdBy"] = user
    Repository.objects.filter(id=id).update(**data)


def updateMR(id: int, datas: dict):
    data = {}
    rangeWord = [
        "merge_id",
        "repo",
        "title",
        "description",
        "state",
        "authoredByEmail",
        "authoredByUserName",
        "authoredAt",
        "reviewedByEmail",
        "reviewedByUserName",
        "reviewedAt",
        "url",
    ]
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "merge_id" in data:
        judgeTypeInt(data["merge_id"])
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
    if "description" in data:
        judgeTypeStr(data["description"])
    if "state" in data:
        if not data["state"] in [i for i in MergeRequest.MRState]:
            raise ParamErr(f"wrong state type.")
    if "authoredByEmail" in data:
        judgeTypeStr(data["authoredByEmail"])
        judgeStrLen(data["authoredByEmail"], 255)
    if "authoredByUserName" in data:
        judgeTypeStr(data["authoredByUserName"])
        judgeStrLen(data["authoredByUserName"], 255)
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "reviewedByEmail" in data:
        judgeTypeStr(data["reviewedByEmail"])
        judgeStrLen(data["reviewedByEmail"], 255)
    if "reviewedByUserName" in data:
        judgeTypeStr(data["reviewedByUserName"])
        judgeStrLen(data["reviewedByUserName"], 255)
    if "reviewedAt" in data:
        judgeTypeFloat(data["reviewedAt"])
    if "url" in data:
        judgeTypeStr(data["url"])
    if "repo" in data:
        judgeTypeInt(data["repo"])
        repo = Repository.objects.filter(id=data["repo"]).first()
        if not repo:
            raise ParamErr(f"wrong repo id.")
        data["repo"] = repo
    MergeRequest.objects.filter(id=id).update(**data)


def updateCommit(id: int, datas: dict):
    rangeWord = [
        "hash_id",
        "repo",
        "title",
        "message",
        "commiter_email",
        "commiter_name",
        "createdAt",
        "url",
    ]
    data = {}
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "hash_id" in data:
        judgeTypeStr(data["hash_id"])
        judgeStrLen(data["hash_id"], 255)
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
    if "message" in data:
        judgeTypeStr(data["message"])
    if "commiter_email" in data:
        judgeTypeStr(data["commiter_email"])
        judgeStrLen(data["commiter_email"], 255)
    if "commiter_name" in data:
        judgeTypeStr(data["commiter_name"])
        judgeStrLen(data["commiter_name"], 255)
    if "createdAt" in data:
        judgeTypeFloat(data["createdAt"])
    if "url" in data:
        judgeTypeStr(data["url"])
    if "repo" in data:
        judgeTypeInt(data["repo"])
        repo = Repository.objects.filter(id=data["repo"]).first()
        if not repo:
            raise ParamErr(f"wrong repo id.")
        data["repo"] = repo
    Commit.objects.filter(id=id).update(**data)


def updateIssue(id: int, datas: dict):
    data = {}
    rangeWord = [
        "issue_id",
        "repo",
        "title",
        "description",
        "state",
        "authoredByUserName",
        "authoredAt",
        "updateAt",
        "closedByUserName",
        "closedAt",
        "assigneeUserName",
        "url",
    ]
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "issue_id" in data:
        judgeTypeInt(data["issue_id"])
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
    if "description" in data:
        judgeTypeStr(data["description"])
    if "state" in data:
        if not data["state"] in [i for i in Issue.IssueState]:
            raise ParamErr(f"wrong type.")
    if "authoredByUserName" in data:
        judgeTypeStr(data["authoredByUserName"])
        judgeStrLen(data["authoredByUserName"], 255)
    if "authoredAt" in data:
        judgeTypeFloat(data["authoredAt"])
    if "updateAt" in data:
        judgeTypeFloat(data["updateAt"])
    if "closedByUserName" in data:
        judgeTypeStr(data["closedByUserName"])
        judgeStrLen(data["closedByUserName"], 255)
    if "closedAt" in data:
        judgeTypeFloat(data["closedAt"])
    if "assigneeUserName" in data:
        judgeTypeStr(data["assigneeUserName"])
        judgeStrLen(data["assigneeUserName"], 255)
    if "url" in data:
        judgeTypeStr(data["url"])
    if "repo" in data:
        judgeTypeInt(data["repo"])
        repo = Repository.objects.filter(id=data["repo"]).first()
        if not repo:
            raise ParamErr(f"wrong repo id.")
        data["repo"] = repo
    Issue.objects.filter(id=id).update(**data)


def updateOperation(proj: Project, type: str, data: dict):
    dataList = require(data, "data")
    if "repo" in data:
        repoId = data["repo"]
        judgeTypeInt(repoId)
    data = require(dataList, "updateData")
    id = require(dataList, "id")
    judgeTypeInt(id)
    updates = {}
    updates.update(data)
    if type == "repo":
        updateRepo(id, data)
    elif type == "commit":
        updateCommit(id, data)
    elif type == "mr":
        updateMR(id, data)
    elif type == "issue":
        updateIssue(id, data)
    return False


def deleteOperation(proj: Project, type: str, data: dict):
    datas = require(data, "data")
    if type == "repo":
        id = require(datas, "id")
        judgeTypeInt(id)
        Repository.objects.filter(id=id).update(disabled=True)
    elif type == "mr":
        id = require(datas, "id")
        judgeTypeInt(id)
        MergeRequest.objects.filter(id=id).update(disabled=True)
    elif type == "issue":
        id = require(datas, "id")
        judgeTypeInt(id)
        Issue.objects.filter(id=id).update(disabled=True)
    elif type == "commit":
        id = require(datas, "id")
        judgeTypeInt(id)
        Commit.objects.filter(id=id).update(disabled=True)
    elif type == "mr-sr":
        mr = require(datas, "MRId")
        judgeTypeInt(mr)
        sr = require(datas, "SRId")
        judgeTypeInt(sr)
        sr = SR.objects.filter(id=sr).first()
        mr = MergeRequest.objects.filter(id=mr).first()
        MRSRAssociation.objects.filter(MR=mr, SR=sr).delete()
    elif type == "issue-sr":
        issue = require(datas, "issueId")
        judgeTypeInt(issue)
        sr = require(datas, "SRId")
        judgeTypeInt(sr)
        sr = SR.objects.filter(id=sr).first()
        issue = Issue.objects.filter(id=issue).first()
        IssueSRAssociation.objects.filter(issue=issue, SR=sr).delete()
    elif type == "commit-sr":
        commit = require(datas, "commitId")
        judgeTypeInt(commit)
        sr = require(datas, "SRId")
        judgeTypeInt(sr)
        sr = SR.objects.filter(id=sr).first()
        commit = Commit.objects.filter(id=commit).first()
        CommitSRAssociation.objects.filter(SR=sr, commit=commit).delete()
    elif type == "issue-mr":
        issue = require(datas, "issueId")
        judgeTypeInt(issue)
        mr = require(datas, "MRId")
        judgeTypeInt(mr)
        IssueMRAssociation.objects.filter(issue__id=issue, MR__id=mr).delete()
    return False

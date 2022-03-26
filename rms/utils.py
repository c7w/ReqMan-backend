from rms.models import *
from ums.models import Project
from ums.utils import *


def serialize(resu: dict, excludeList: list = []):
    return [model_to_dict(p, exclude=excludeList) for p in resu]


def getIR(proj: Project):
    return IR.objects.filter(project=proj, disabled=False).order_by("rank")


def getSR(proj: Project):
    return SR.objects.filter(project=proj, disabled=False).order_by("rank")


def getIeration(proj: Project):
    return Iteration.objects.filter(project=proj, disabled=False).order_by("sid")


def getService(proj: Project):
    return Service.objects.filter(project=proj, disabled=False).order_by("rank")


def getUserIteration(proj: Project):
    Itera = getIeration(proj)
    association = []
    for i in Itera:
        association.append(UserIterationAssociation.objects.filter(iteration=i).first())
    return association


def getSRIteration(proj: Project):
    Itera = getIeration(proj)
    association = []
    for i in Itera:
        association.extend(SRIterationAssociation.objects.filter(iteration=i))
    return association


def getIRSR(proj: Project):
    IRs = getIR(proj)
    SRs = getSR(proj)
    return IRSRAssociation.objects.filter(IR__in=IRs, SR__in=SRs)


def judgeTypeInt(data):
    if type(data) == int:
        return
    else:
        raise ParamErr(f"wrong Int type in {data}")


def judgeTypeStr(data):
    if type(data) == str:
        return
    else:
        raise ParamErr(f"wrong String type in {data}.")


def judgeTypeFloat(data):
    if type(data) == float:
        return
    else:
        raise ParamErr(f"wrong Float type in {data}.")


def createIR(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["description"] = require(datas, "description")
    judgeTypeStr(data["description"])
    data["rank"] = require(datas, "rank")
    judgeTypeInt(data["rank"])
    data["createdBy"] = require(datas, "createdBy")
    IR.objects.create(**data)


def createSR(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["description"] = require(datas, "description")
    judgeTypeStr(data["description"])
    data["rank"] = require(datas, "rank")
    judgeTypeInt(data["rank"])
    data["priority"] = require(datas, "priority")
    judgeTypeInt(data["priority"])
    data["createdBy"] = require(datas, "createdBy")
    data["state"] = require(datas, "state")
    if not data["state"] in ["TODO", "WIP", "Reviewing", "Done"]:
        raise ParamErr(f"wrong type.")
    SR.objects.create(**data)


def createIteration(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["sid"] = require(datas, "sid")
    judgeTypeInt(data["sid"])
    data["begin"] = require(datas, "begin")
    judgeTypeFloat(data["begin"])
    data["end"] = require(datas, "end")
    judgeTypeFloat(data["end"])
    Iteration.objects.create(**data)


def createService(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["description"] = require(datas, "description")
    judgeTypeStr(data["description"])
    data["rank"] = require(datas, "rank")
    judgeTypeInt(data["rank"])
    data["createdBy"] = require(datas, "createdBy")
    Service.objects.create(**data)


def createIRSRAssociation(datas: dict):
    ir = require(datas, "IRId")
    judgeTypeInt(ir)
    sr = require(datas, "SRId")
    judgeTypeInt(sr)
    ir = IR.objects.filter(id=ir).first()
    sr = SR.objects.filter(id=sr).first()
    if not ir or not sr:
        raise ParamErr(f"wrong IR/SR Id.")
    data = {"IR": ir, "SR": sr}
    IRSRAssociation.objects.create(**data)


def createUserIterationAssociation(datas: dict):
    it = require(datas, "iterationId")
    judgeTypeInt(it)
    it = Iteration.objects.filter(id=it).first()
    user = require(datas, "userId")
    judgeTypeInt(user)
    user = User.objects.filter(id=user).first()
    if not user or not it:
        raise ParamErr(f"wrong It/User Id.")
    data = {"user": user, "iteration": it}
    UserIterationAssociation.objects.create(**data)


def createSRIterationAssociation(datas: dict):
    sr = require(datas, "SRId")
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    it = require(datas, "iterationId")
    judgeTypeInt(it)
    it = Iteration.objects.filter(id=it).first()
    if not it or not sr:
        raise ParamErr(f"wrong It/SR Id.")
    data = {"SR": sr, "iteration": it}
    SRIterationAssociation.objects.create(**data)


def createOperation(proj: Project, type: string, data: dict, user: User):
    dataList = require(data, "data")
    data = require(dataList, "updateData")
    create = {}
    create.update(data)
    create["project"] = proj
    create["createdBy"] = user

    if type == "ir":
        createIR(create)
    elif type == "sr":
        createSR(create)
    elif type == "iteration":
        createIteration(create)
    elif type == "ir-sr":
        createIRSRAssociation(create)
    elif type == "sr-iteration":
        createSRIterationAssociation(create)
    elif type == "service":
        createService(create)
    elif type == "user-iteration":
        createUserIterationAssociation(create)
    return False


def updateIR(id: int, datas: dict):
    data = {}
    for i in datas:
        if i == "title":
            data["title"] = datas[i]
            judgeTypeStr(data["title"])
        elif i == "description":
            data["description"] = datas[i]
            judgeTypeStr(data["description"])
        elif i == "rank":
            data[i] = datas[i]
            judgeTypeInt(data["rank"])
    IR.objects.filter(id=id).update(**data)


def updateSR(id: int, datas: dict):
    rangeWord = ["title", "description", "rank", "priority", "state"]
    data = {}
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "title" in data:
        judgeTypeStr(data["title"])
    if "description" in data:
        judgeTypeStr(data["description"])
    if "rank" in data:
        judgeTypeInt(data["rank"])
    if "priority" in data:
        judgeTypeInt(data["priority"])
    if "state" in data:
        if not data["state"] in ["TODO", "WIP", "Reviewing", "Done"]:
            raise ParamErr(f"wrong type.")
    SR.objects.filter(id=id).update(**data)


def updateIteration(id: int, datas: dict):
    rangeWord = ["title", "sid", "begin", "end"]
    data = {}
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "title" in data:
        judgeTypeStr(data["title"])
    if "sid" in data:
        judgeTypeInt(data["sid"])
    if "begin" in data:
        judgeTypeFloat((data["begin"]))
    if "end" in data:
        judgeTypeFloat(data["end"])
    Iteration.objects.filter(id=id).update(**data)


def updateService(id: int, datas: dict):
    data = {}
    for i in datas:
        if i == "title":
            data["title"] = datas[i]
            judgeTypeStr(data["title"])
        elif i == "description":
            data["description"] = datas[i]
            judgeTypeStr(data["description"])
        elif i == "rank":
            data[i] = datas[i]
            judgeTypeInt(data["rank"])
    Service.objects.filter(id=id).update(**data)


def updateOperation(proj: Project, type: string, data: dict):
    dataList = require(data, "data")
    data = require(dataList, "updateData")
    updates = {}
    updates.update(data)
    id = require(dataList, "id")
    judgeTypeInt(id)
    if type == "ir":
        updateIR(id, data)
    elif type == "sr":
        updateSR(id, data)
    elif type == "iteration":
        updateIteration(id, data)
    elif type == "service":
        updateService(id, data)
    return False


def deleteOperation(proj: Project, type: string, data: dict):
    dataList = require(data, "data")
    if type == "ir":
        id = require(dataList, "id")
        judgeTypeInt(id)
        IR.objects.filter(id=id).update(disabled=True)
    elif type == "sr":
        id = require(dataList, "id")
        judgeTypeInt(id)
        SR.objects.filter(id=id).update(disabled=True)
    elif type == "iteration":
        id = require(dataList, "id")
        judgeTypeInt(id)
        Iteration.objects.filter(id=id).update(disabled=True)
    elif type == "ir-sr":
        IRId = require(dataList, "IRId")
        SRId = require(dataList, "SRId")
        judgeTypeInt(IRId)
        judgeTypeInt(SRId)
        sr = SR.objects.filter(id=SRId).first()
        ir = IR.objects.filter(id=IRId).first()
        IRSRAssociation.objects.filter(SR=sr, IR=ir).delete()
    elif type == "sr-iteration":
        iterationId = require(dataList, "iterationId")
        judgeTypeInt(iterationId)
        SRId = require(dataList, "SRId")
        judgeTypeInt(SRId)
        iteration = Iteration.objects.filter(id=iterationId).first()
        sr = SR.objects.filter(id=SRId).first()
        SRIterationAssociation.objects.filter(iteration=iteration, SR=sr).delete()
    elif type == "service":
        id = require(dataList, "id")
        judgeTypeInt(id)
        Service.objects.filter(id=id).update(disabled=True)
    elif type == "user-iteration":
        iterationId = require(dataList, "iterationId")
        judgeTypeInt(iterationId)
        iteration = Iteration.objects.filter(id=iterationId).first()
        UserIterationAssociation.objects.filter(iteration=iteration).delete()
    return False

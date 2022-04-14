from tkinter.tix import Tree
from rms.models import *
from ums.models import Project
from ums.utils import *


def serialize(resu: dict, excludeList=None):
    if excludeList is None:
        excludeList = []
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
        association.extend(UserIterationAssociation.objects.filter(iteration=i))
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


def getServiceSR(proj: Project):
    SRs = getSR(proj)
    services = getService(proj)
    return ServiceSRAssociation.objects.filter(SR__in=SRs, service__in=services)


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


def judgeStrLen(data, lens):
    if len(data) > lens:
        raise ParamErr(f"Beyond length limite in {data} .")
    else:
        return


def getServiceOfSR(proj: Project, SRId: int):
    sr = SR.objects.filter(id=SRId).first()
    relation = ServiceSRAssociation.objects.filter(SR=sr).first()
    return [relation.service]


def getSROfService(proj: Project, ServiceId: int):
    service = Service.objects.filter(id=ServiceId).first()
    relation = ServiceSRAssociation.objects.filter(service=service).all()
    services = []
    for i in relation:
        services.append(i.SR)
    return services


def getIRIteration(proj: Project):
    IR = getIR(proj)
    return IRIterationAssociation.objects.filter(IR__in=IR)


def getProjectIteration(proj: Project):
    return ProjectIterationAssociation.objects.filter(project=proj)


def getSRChangeLog(srId: int):
    return SR_Changelog.objects.filter(SR__id=srId)


def getUserSR(proj: Project):
    SRs = getSR(proj)
    return UserSRAssociation.objects.filter(sr__in=SRs)


def createIR(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    judgeStrLen(data["title"], 255)
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
    judgeStrLen(data["title"], 255)
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
    judgeStrLen(data["title"], 255)
    Iteration.objects.create(**data)


def createService(datas: dict):
    data = {}
    data["project"] = require(datas, "project")
    data["title"] = require(datas, "title")
    judgeTypeStr(data["title"])
    data["description"] = require(datas, "description")
    judgeStrLen(data["title"], 255)
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
    exist = IRSRAssociation.objects.filter(IR=ir, SR=sr).first()
    if exist:
        raise ParamErr("Association Exist")
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
    exist = UserIterationAssociation.objects.filter(user=user, iteration=it).first()
    if exist:
        raise ParamErr("Association Exist")
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
    exist = SRIterationAssociation.objects.filter(SR=sr, iteration=it).first()
    if exist:
        raise ParamErr("Association Exist")
    SRIterationAssociation.objects.create(**data)


def createServiceSRAssociation(datas: dict):
    sr = require(datas, "SRId")
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    exist = ServiceSRAssociation.objects.filter(SR=sr).first()
    if exist:
        raise ParamErr(f"SR connected!")
    service = require(datas, "serviceId")
    judgeTypeInt(service)
    service = Service.objects.filter(id=service).first()
    if not sr or not service:
        raise ParamErr(f"wrong service/SR Id.")
    data = {
        "SR": sr,
        "service": service,
    }
    exist = ServiceSRAssociation.objects.filter(SR=sr, service=service).first()
    if exist:
        raise ParamErr("Association Exist")
    ServiceSRAssociation.objects.create(**data)


def createIRIteration(datas: dict):
    ir = require(datas, "IRId")
    judgeTypeInt(ir)
    ir = IR.objects.filter(id=ir).first()
    it = require(datas, "iterationId")
    judgeTypeInt(it)
    it = Iteration.objects.filter(id=it).first()
    if not ir or not it:
        raise ParamErr(f"wrong It/IR Id.")
    exist = IRIterationAssociation.objects.filter(IR=ir, iteration=it).first()
    if exist:
        return
    data = {"IR": ir, "iteration": it}
    exist = IRIterationAssociation.objects.filter(IR=ir, iteration=it).first()
    if exist:
        raise ParamErr("Association Exist")
    IRIterationAssociation.objects.create(**data)


def createProjectIteration(datas: dict):
    it = require(datas, "iterationId")
    judgeTypeInt(it)
    it = Iteration.objects.filter(id=it).first()
    if not it:
        raise ParamErr(f"wrong It Id.")
    exist = ProjectIterationAssociation.objects.filter(project=datas["project"]).first()
    if exist:
        raise ParamErr(f"Project connected!")
    data = {"project": datas["project"], "iteration": it}
    exist = ProjectIterationAssociation.objects.filter(
        project=datas["project"], iteration=it
    ).first()
    if exist:
        raise ParamErr("Association Exist")
    ProjectIterationAssociation.objects.create(**data)


def createUserSR(datas: dict):
    user = require(datas, "userId")
    judgeTypeInt(user)
    user = User.objects.filter(id=user).first()
    if not user:
        raise ParamErr("Wrong user Id.")
    sr = require(datas, "SRId")
    judgeTypeInt(sr)
    sr = SR.objects.filter(id=sr).first()
    if not sr:
        raise ParamErr("Wrong sr Id")
    exist = UserSRAssociation.objects.filter(sr=sr).first()
    if exist:
        raise ParamErr(f"Association to {sr.id} exist.")
    data = {"user": user, "sr": sr}
    UserSRAssociation.objects.create(**data)


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
    elif type == "service-sr":
        createServiceSRAssociation(create)
    elif type == "ir-iteration":
        createIRIteration(create)
    elif type == "project-iteration":
        createProjectIteration(create)
    elif type == "user-sr":
        createUserSR(create)
    else:
        return True
    return False


def updateIR(id: int, datas: dict):
    data = {}
    for i in datas:
        if i == "title":
            data["title"] = datas[i]
            judgeTypeStr(data["title"])
            judgeStrLen(data["title"], 255)
        elif i == "description":
            data["description"] = datas[i]
            judgeTypeStr(data["description"])
        elif i == "rank":
            data[i] = datas[i]
            judgeTypeInt(data["rank"])
    IR.objects.filter(id=id).update(**data)


def updateSR(id: int, datas: dict, user: User):
    print("HERE")
    rangeWord = ["title", "description", "rank", "priority", "state"]
    data = {}
    log = {}
    sr = SR.objects.filter(id=id).first()
    if not sr:
        raise ParamErr(f"Wrong SR Id.")
    log["SR"] = sr
    log["project"] = sr.project
    log["formerState"] = sr.state
    log["formerDescription"] = sr.description
    log["changedBy"] = user
    log["description"] = "Changed by " + user.name
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
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
    SR_Changelog.objects.create(**log)


def updateIteration(id: int, datas: dict):
    rangeWord = ["title", "sid", "begin", "end"]
    data = {}
    for i in datas:
        if i in rangeWord:
            data[i] = datas[i]
    if "title" in data:
        judgeTypeStr(data["title"])
        judgeStrLen(data["title"], 255)
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
            judgeStrLen(data["title"], 255)
        elif i == "description":
            data["description"] = datas[i]
            judgeTypeStr(data["description"])
        elif i == "rank":
            data[i] = datas[i]
            judgeTypeInt(data["rank"])
    Service.objects.filter(id=id).update(**data)


def updateOperation(proj: Project, type: string, data: dict, user: User):
    dataList = require(data, "data")
    data = require(dataList, "updateData")
    updates = {}
    updates.update(data)
    id = require(dataList, "id")
    judgeTypeInt(id)
    if type == "ir":
        updateIR(id, data)
    elif type == "sr":
        updateSR(id, data, user)
    elif type == "iteration":
        updateIteration(id, data)
    elif type == "service":
        updateService(id, data)
    else:
        return True
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
        userId = require(dataList, "userId")
        judgeTypeInt(userId)
        user = User.objects.filter(id=userId).first()
        UserIterationAssociation.objects.filter(iteration=iteration, user=user).delete()
    elif type == "service-sr":
        sr = require(dataList, "SRId")
        judgeTypeInt(sr)
        sr = SR.objects.filter(id=sr).first()
        service = require(dataList, "serviceId")
        judgeTypeInt(service)
        service = Service.objects.filter(id=service).first()
        ServiceSRAssociation.objects.filter(SR=sr, service=service).delete()
    elif type == "ir-iteration":
        ir = require(dataList, "IRId")
        judgeTypeInt(ir)
        ir = IR.objects.filter(id=ir).first()
        it = require(dataList, "iterationId")
        judgeTypeInt(it)
        it = Iteration.objects.filter(id=it).first()
        IRIterationAssociation.objects.filter(IR=ir, iteration=it).delete()
    elif type == "project-iteration":
        it = require(dataList, "iterationId")
        judgeTypeInt(it)
        it = Iteration.objects.filter(id=it).first()
        ProjectIterationAssociation.objects.filter(project=proj, iteration=it).delete()
    elif type == "user-sr":
        user = require(dataList, "userId")
        judgeTypeInt(user)
        sr = require(dataList, "SRId")
        judgeTypeInt(sr)
        UserSRAssociation.objects.filter(user__id=user, sr__id=sr).delete()
    return False

from faulthandler import disable
from rms.models import *
from ums.models import Project
from ums.utils import *

def getIR(proj:Project):
    return IR.objects.filter(project=proj,disabled=False).order_by('rank')

def getSR(proj:Project):
    return SR.objects.filter(project=proj,disabled=False).order_by('rank')

def getIeration(proj:Project):
    return Iteration.objects.filter(project=proj,disabled=False).order_by('sid')

def getService(proj:Project):
    return Service.objects.filter(project=proj,disabled=False).order_by('rank')

def getUserIteration(proj:Project):
    Itera = getIeration(proj)
    association = []
    for i in Itera:
        association.append(UserIterationAssociation.objects.filter(iteration=i).first())
    return association

def getSRIteration(proj:Project):
    Itera = getIeration(proj)
    association = []
    for i in Itera:
        association.extend(SRIterationAssociation.objects.filter(iteration=i))
    return association

def getIRSR(proj:Project):
    IRs = getIR(proj)
    SRs = getSR(proj)
    return IRSRAssociation.objects.filter(IR__in= IRs ,SR__in =SRs)



def createIR(data:dict):
    IR.objects.create(**data)

def createSR(data:dict):
    SR.objects.create(**data)

def createIteration(data:dict):
    Iteration.objects.create(**data)

def createService(data:dict):
    Service.objects.create(**data)

def createIRSRAssociation(data:dict):
    IRSRAssociation.objects.create(**data)

def createUserIterationAssociation(data:dict):
    UserIterationAssociation.objects.create(**data)

def createSRIterationAssociation(data:dict):
    SRIterationAssociation.objects.create(**data)

def createOperation(proj:Project,type:string,data:dict):
    dataList = require(data,'data')
    data = require(dataList,'updateData')
    create = {}
    create.update(data)
    create['project']=proj

    if type == 'ir':
        createIR(create)
    elif type == 'sr':
        createSR(create)
    elif type == 'iteration':
        createIteration(create)
    elif type == 'ir-sr':
        createIRSRAssociation(create)
    elif type == 'sr-iteration':
        createSRIterationAssociation(create)
    elif type == 'service':
        createService(create)
    elif type == 'user-iteration':
        createUserIterationAssociation(create)
    return False

def updateIR(id:int,data:dict):
    IR.objects.filter(id=id).update(**data)

def updateSR(id:int,data:dict):
    SR.objects.filter(id=id).update(**data)

def updateIteration(id:int,data:dict):
    Iteration.objects.filter(id=id).update(**data)

def updateService(id:int,data:dict):
    Service.objects.filter(id=id).update(**data)

def updateOperation(proj:Project,type:string,data:dict):
    dataList = require(data,'data')
    data = require(dataList,'updateData')
    updates = {}
    updates.update(data)
    id = require(dataList,"id")
    if type == 'ir':
        updateIR(id,data)
    elif type == 'sr':
        updateSR(id,data)
    elif type == 'iteration':
        updateIteration(id,data)
    elif type == 'service':
        updateService(id,data)
    return False

def deleteOperation(proj:Project,type:string,data:dict):
    dataList = require(data,'data')
    if type == 'ir':
        id = require(dataList,'id')
        IR.objects.filter(id=id).update(disabled=True)
    elif type == 'sr':
        id = require(dataList,'id')
        SR.objects.filter(id=id).update(disabled=True)
    elif type == 'iteration':
        id = require(dataList,'id')
        Iteration.objects.filter(id=id).update(disabled=True)
    elif type == 'ir-sr':
        IRId = require(dataList,'IRId')
        SRId = require(dataList,'SRId')
        sr = SR.objects.filter(id=SRId).first()
        ir = IR.objects.filter(id=IRId).first()
        IRSRAssociation.objects.filter(
            SR=sr,
            IR=ir
        ).delete()
    elif type == 'sr-iteration':
        iterationId = require(dataList,'iterationId')
        SRId = require(dataList,'SRId')
        iteration = Iteration.objects.filter(id=iterationId).first()
        sr = SR.objects.filter(id=SRId).first()
        SRIterationAssociation.objects.filter(
            iteration=iteration,
            SR=sr
        ).delete()
    elif type == 'service':
        id = require(dataList,'id')
        Service.objects.filter(id=id).update(disabled=True)
    elif type == 'user-iteration':
        iterationId = require(dataList,'iterationId')
        iteration = Iteration.objects.filter(id=iterationId).first()
        UserIterationAssociation.objects.filter(
            iteration=iteration
        ).delete()
    return False

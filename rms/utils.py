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
    return IRSRAssociation.objects.filter(IR in IRs ,SR in SRs)



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
    if not dataList:
        return True
    data = require(dataList,'updateData')
    if not data:
        return True
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

        
from rms.models import *
from ums.models import Project
from ums.utils import *

def getIR(proj:Project):
    return IR.objects.filter(project=proj).order_by('rank')

def getSR(proj:Project):
    return SR.objects.filter(project=proj).order_by('rank')

def getIeration(proj:Project):
    return Iteration.objects.filter(project=proj).order_by('sid')

def getService(proj:Project):
    return Service.objects.filter(project=proj).order_by('rank')

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
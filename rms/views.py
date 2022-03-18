from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from ums.views import FAIL
from ums.views import SUCC
from utils.sessions import SessionAuthentication
from ums.utils import *
from rms.utils import *

class RMSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    def serialize(self,resu:dict,excludeList:list=[]):
        return [model_to_dict(p,exclude=excludeList) for p in resu] 

    def projectGET(self,req:Request):
        proj = intify(require(req.query_params,'project'))
        proj = proj_exist(proj)
        if not proj:
            return FAIL
        if not in_proj(req.user,proj):
            return FAIL
        type = require(req.query_params,'type')

        resu = []
        if type == 'ir':
            resu =  self.serialize(getIR(proj),['SR'])
        elif type == 'sr':
            resu = self.serialize(getSR(proj),['IR'])
        elif type == 'iteration':
            resu = self.serialize(getIeration(proj))
        elif type == 'ir-sr':
            resu = self.serialize(getIRSR(proj))
        elif type == 'sr-iteration':
            resu = self.serialize(getSRIteration(proj))
        elif type == 'service':
            resu = self.serialize(getService(proj))
        elif type == 'user-iteration':
            resu = self.serialize(getUserIteration(proj))
        else:
            return FAIL
        print(resu)
        return Response({
            'code':0,
            'data':resu
        })

    def projectPOST(self,req:Request):
        proj = intify(require(req.data,'project'))
        proj = proj_exist(proj)
        if not proj:
            return FAIL
        if not is_role(req.user,proj,Role.SYS):
            return FAIL
        
        operation = require(req.data,'operation')

        type = require(req.data,'type')

        isFail = False
        if operation =='create':
            isFail = createOperation(proj,type,req.data,req.user)
        elif operation == 'update':
            isFail = updateOperation(proj,type,req.data)
        if operation == 'delete':
            isFail = deleteOperation(proj,type,req.data)
        if isFail:
            return FAIL
        else:
            return SUCC

    @action(detail=False,methods=['POST','GET'])
    def project(self,req:Request):
        if req.method == 'POST':
            return RMSViewSet.projectPOST(self,req)
        elif req.method == 'GET':
            return RMSViewSet.projectGET(self,req)
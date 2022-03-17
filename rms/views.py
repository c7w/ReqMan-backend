from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from ums.views import FAIL
from utils.sessions import SessionAuthentication
from ums.utils import *
from rms.utils import *


class RMSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    @action(detail=False)
    def project(sef,req:Request):
        proj = intify(require(req.data,'project'))
        proj = proj_exist(proj)
        if not proj:
            return FAIL
        
        if not in_proj(req.user,proj):
            return FAIL

        type = require(req.data,'type')
        if not type:
            return FAIL
        
        resu = []
        if type == 'ir':
            resu = getIR(proj)
        elif type == 'sr':
            resu = getSR(proj)
        elif type == 'iteration':
            resu = getIeration(proj)
        elif type == 'ir-sr':
            resu = getIRSR(proj)
        elif type == 'sr-iteration':
            resu = getSRIteration(proj)
        elif type == 'service':
            resu = getService(proj)
        elif type == 'user-iteration':
            resu = getUserIteration(proj)
        
        return Response({
            'code':0,
            'data':resu
        })


    @action(detail=False,methods=['POST'])
    def project(self,req:Request):
        pass
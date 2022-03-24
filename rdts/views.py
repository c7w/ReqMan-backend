from urllib.request import Request
from rest_framework import viewsets
from rdts.utlis import getRepo, repoExist
from ums.utils import in_proj, intify, proj_exist, require
from ums.views import FAIL
from utils.sessions import SessionAuthentication
from rest_framework.decorators import action
from rms.utils import serialize

class RDTSViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    def projectGET(self,req:Request):
        resu = []
        type = require(req.query_param,'type')
        if type == 'repo':
            proj = intify(require(req.query_params,"project"))
            proj = proj_exist(proj)
            if not proj:
                return FAIL
            if not in_proj(req.user,proj):
                return FAIL
            resu = serialize(getRepo(proj))
            return resu
        repo = intify(require(req.query_params,"repo"))
        repo = repoExist(repo)
        if not repo:
            return FAIL
        if type == 'mr':
            resu = serialize

    def projectPOST(self,req:Request):
        pass

    @action(detail=False,methods=["POST","GET"])
    def project(self,req:Request):
        if req.method == 'POST':
            return self.projectPOST(req)
        elif req.method == 'GET':
            return self.projectGET(req)
        else:
            return FAIL
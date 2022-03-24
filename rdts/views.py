from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rdts.utlis import getCommit, getCommitSR, getIssue, getIssueSR, getMR, getMRSR, getRepo, repoExist
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
            resu = serialize(getMR(repo))
        elif type == 'commit':
            resu = serialize(getCommit(repo))
        elif type == 'issue':
            resu = serialize(getIssue(repo))
        elif type == 'commit-sr':
            resu = serialize(getCommitSR(repo))
        elif type == 'mr-sr':
            resu = serialize(getMRSR(repo))
        elif type == 'issue-sr':
            resu = serialize(getIssueSR(repo))
        else:
            return FAIL
        return Response({'code':0,'data':resu})
        

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
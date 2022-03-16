import datetime
import random
import string
from ums.models import SessionPool, EXPIRE_DAYS, User
from rest_framework import authentication, exceptions, status
from rest_framework.request import Request

class SessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, req: Request):
        session_id = getSessionId(req)
        if not session_id:
            raise exceptions.AuthenticationFailed('Request without a sessionId')
        return (verifySessionId(session_id), session_id)

def getSessionId(request):
    return request.COOKIES.get('sessionId')

def setSessionId(response):
    sessionId = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    response.set_cookie('sessionId', sessionId, expires=60 * 60 * 24 * EXPIRE_DAYS)
    return response

def verifySessionId(sessionId):
    sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
    if sessionRecord:
        if sessionRecord.expireAt < datetime.datetime.now():
            SessionPool.objects.filter(sessionId=sessionId).delete()
            return None
        return sessionRecord.user
    else:
        return None

def bind(sessionId: str, user: User):
    SessionPool.objects.create(sessionId=sessionId, user=user)

def disable(sessionId: str):
    record = SessionPool.objects.filter(sessionId).first()
    if record:
        record.delete()

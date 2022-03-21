import random
import string
import datetime as dt
import pytz
from backend.settings import TIME_ZONE
from ums.models import SessionPool, EXPIRE_DAYS, User
from rest_framework import authentication, exceptions, status
from rest_framework.request import Request

class SessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, req: Request):
        session_id = get_session_id(req)
        if not session_id:
            raise exceptions.AuthenticationFailed('Request without a sessionId')
        return (verify_session_id(session_id), session_id)

def get_session_id(request):
    if request.method == 'POST':
        return request.data.get('sessionId')
    return request.GET.get('sessionId')

def set_session_id(response):
    sessionId = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    response.set_cookie('sessionId', sessionId, expires=60 * 60 * 24 * EXPIRE_DAYS)
    return response

def verify_session_id(sessionId):
    sessionRecord = SessionPool.objects.filter(sessionId=sessionId).first()
    if sessionRecord:
        if sessionRecord.expireAt < dt.datetime.now(pytz.timezone(TIME_ZONE)):
            SessionPool.objects.filter(sessionId=sessionId).delete()
            return None
        return sessionRecord.user
    else:
        return None

def bind_session_id(sessionId: str, user: User):
    SessionPool.objects.create(sessionId=sessionId, user=user)

def disable_session_id(sessionId: str):
    record = SessionPool.objects.filter(sessionId=sessionId).first()
    if record:
        record.delete()

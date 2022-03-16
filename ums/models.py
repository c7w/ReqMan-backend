from django.db import models
import datetime as dt
import pytz
from backend.settings import TIME_ZONE

EXPIRE_DAYS = 3

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(unique=True)
    password = models.TextField()
    email = models.TextField()
    avatar = models.TextField(default='')
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(default=dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE))))

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

class SessionPool(models.Model):
    sessionId = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(default=dt.datetime.now() + dt.timedelta(days=EXPIRE_DAYS))

from django.db import models
import datetime as dt
import pytz
from backend.settings import TIME_ZONE

EXPIRE_DAYS = 3

class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.TextField()
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(default=dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE))))
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['description']),
        ]

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(unique=True)
    password = models.TextField()
    email = models.TextField()
    avatar = models.TextField(default='')
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(default=dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE))))
    project = models.ManyToManyField(Project, through='UserProjectAssociation')

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

class SessionPool(models.Model):
    sessionId = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(default=dt.datetime.now() + dt.timedelta(days=EXPIRE_DAYS))

    class Mata:
        indexes = [
            models.Index(fields=['sessionId'])
        ]

class UserProjectAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)

    class Meta:
        unique_together = ['user', 'project']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['user']),
            models.Index(fields=['user', 'project'])
        ]


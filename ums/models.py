from django.db import models
import datetime as dt
import pytz
from backend.settings import TIME_ZONE
import utils.model_date as getTime

EXPIRE_DAYS = 2


class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(
        default=getTime.get_timestamp()
    )

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    password = models.TextField()
    email = models.CharField(max_length=255, unique=True)
    avatar = models.TextField(default="")
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(
        default=getTime.get_timestamp()
    )
    project = models.ManyToManyField(Project, through="UserProjectAssociation")

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["email"]),
        ]


class SessionPool(models.Model):
    sessionId = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(
        default=getTime.get_datetime()
    )

    class Mata:
        indexes = [models.Index(fields=["sessionId"])]


class Role(models.TextChoices):
    MEMBER = "member"
    DEV = "dev"
    QA = "qa"
    SYS = "sys"
    SUPERMASTER = "supermaster"


class UserProjectAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.TextField(choices=Role.choices)

    class Meta:
        unique_together = ["user", "project"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["user"]),
            models.Index(fields=["user", "project"]),
        ]


class ProjectInvitationAssociation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    invitation = models.CharField(max_length=64)
    role = models.TextField(choices=Role.choices)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["invitation"]),
        ]

from django.db import models
import datetime as dt
import pytz
from backend.settings import TIME_ZONE
import utils.model_date as getTime

EXPIRE_DAYS = 2
PROJECT_TITLE_LEN = 255
PROJECT_DESC_LEN = 1000


class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    avatar = models.TextField(default="")
    remote_sr_pattern_extract = models.TextField(
        default="(?<=\[)SR.\d{3}.\d{3}(?=(.[I/F/B])?])"
    )
    remote_issue_iid_extract = models.TextField(default="(?<=\(#)\d+(?=\))")

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    password = models.TextField()
    email = models.CharField(max_length=255)
    avatar = models.TextField(default="")
    disabled = models.BooleanField(default=False)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    project = models.ManyToManyField(Project, through="UserProjectAssociation")
    email_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["email"]),
        ]


class SessionPool(models.Model):
    sessionId = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expireAt = models.DateTimeField(default=getTime.get_datetime)

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
    role = models.CharField(max_length=12, choices=Role.choices)

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
    role = models.CharField(max_length=12, choices=Role.choices)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["invitation"]),
        ]


class PendingModifyPasswordEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.TextField()
    hash1 = models.CharField(max_length=100, unique=True)
    hash2 = models.CharField(max_length=100, default="")
    createdAt = models.FloatField(default=getTime.get_timestamp)
    beginAt = models.FloatField(default=-1)
    hash1_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["hash1"]),
            models.Index(fields=["hash2"]),
        ]


class PendingVerifyEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.TextField()
    hash = models.CharField(max_length=100, unique=True)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    is_major = models.BooleanField()

    class Meta:
        indexes = [models.Index(fields=["hash"])]


class UserMinorEmailAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["email"]),
        ]


class UserRemoteUsernameAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remote_name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    class Meta:
        indexes = [models.Index(fields=["remote_name", "url"])]


class Config(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        indexes = [models.Index(fields=["key"])]

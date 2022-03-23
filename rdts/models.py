import datetime as dt
from email import message
from secrets import choice
import pytz
from backend.settings import TIME_ZONE
from django.db import models


class Repository(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.CharField(max_length=255)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    createdBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    createdAt = models.FloatField(
        default=dt.datetime.timestamp(dt.datetime.now(pytz.timezone(TIME_ZONE)))
    )
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["title"]),
            models.Index(fields=["title", "project"]),
        ]
        unique_together = ["project", "title"]


class Commit(models.Model):
    id = models.BigAutoField(primary_key=True)
    hash_id = models.CharField(max_length=255)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    commiter_email = models.CharField(max_length=255)
    createdAt = models.FloatField()
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["commiter_email"])]


class MergeRequest(models.Model):
    id = models.AutoField(primary_key=True)
    merge_id = models.IntegerField()
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    class MRState(models.TextChoices):
        MERGED = "Merged"
        ClOSED = "closed"
        OPENED = "opened"

    state = models.TextField(choices=MRState.choices)
    authoredByEmail = models.CharField(max_length=255)
    authoredAt = models.FloatField(null=True, blank=True)
    reviewedByEmail = models.CharField(max_length=255)
    reviewedAt = models.FloatField(null=True, blank=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["authoredByEmail"]),
            models.Index(fields=["reviewedByEmail"]),
        ]


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    issue_id = models.IntegerField()
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    class IssueState(models.TextChoices):
        ClOSED = "closed"
        OPENED = "opened"

    state = models.TextField(choices=IssueState.choices)
    authoredByEmail = models.CharField(max_length=255)
    authoredAt = models.FloatField(null=True, blank=True)
    reviewedByEmail = models.CharField(max_length=255)
    reviewedAt = models.FloatField(null=True, blank=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["authoredByEmail"]),
            models.Index(fields=["reviewedByEmail"]),
        ]


class CommitSRAssociation(models.Model):
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)


class MRSRAssociation(models.Model):
    MR = models.ForeignKey(MergeRequest, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)


class IssueSRAssociation(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)

class RemoteRepo(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=50)
    remote_id = models.TextField()
    access_token = models.TextField()

class CrawlLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    repo = models.ForeignKey(RemoteRepo, on_delete=models.CASCADE)
    time = models.FloatField()

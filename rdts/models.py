import datetime as dt
from email import message
from secrets import choice
import pytz
from backend.settings import TIME_ZONE
from django.db import models
import utils.model_date as getTime


class Repository(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.CharField(max_length=255)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    createdAt = models.FloatField(default=getTime.get_timestamp)
    createdBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["title", "project"]),
            models.Index(fields=["project"]),
            models.Index(fields=["title"]),
            models.Index(fields=["url"]),
        ]


class Commit(models.Model):
    id = models.BigAutoField(primary_key=True)
    hash_id = models.CharField(max_length=255)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.TextField()
    message = models.TextField()
    commiter_email = models.CharField(max_length=255)
    commiter_name = models.CharField(max_length=255)
    createdAt = models.FloatField()
    url = models.TextField()
    disabled = models.BooleanField(default=False)
    commite_date = models.FloatField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["commiter_email"]),
            models.Index(fields=["repo"]),
        ]

    user_committer = models.ForeignKey(
        "ums.User", on_delete=models.CASCADE, null=True, default=None, related_name="+"
    )
    # diff = models.TextField(default="")
    additions = models.IntegerField(default=-1)
    deletions = models.IntegerField(default=-1)


class MergeRequest(models.Model):
    id = models.AutoField(primary_key=True)
    merge_id = models.IntegerField()
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    class MRState(models.TextChoices):
        MERGED = "merged"
        ClOSED = "closed"
        OPENED = "opened"

    state = models.TextField(choices=MRState.choices)
    authoredByEmail = models.CharField(max_length=255, default="")
    authoredByUserName = models.CharField(max_length=255, default="")
    authoredAt = models.FloatField(null=True, blank=True)
    reviewedByEmail = models.CharField(max_length=255, default="")
    reviewedByUserName = models.CharField(max_length=255, default="")
    reviewedAt = models.FloatField(null=True, blank=True)
    disabled = models.BooleanField(default=False)
    url = models.TextField()

    user_authored = models.ForeignKey(
        "ums.User", on_delete=models.CASCADE, null=True, default=None, related_name="+"
    )
    user_reviewed = models.ForeignKey(
        "ums.User", on_delete=models.CASCADE, null=True, default=None, related_name="+"
    )

    updated_at = models.FloatField(null=True, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["authoredByUserName"]),
            models.Index(fields=["reviewedByUserName"]),
            models.Index(fields=["repo"]),
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
    authoredByUserName = models.CharField(max_length=255, default="")
    authoredAt = models.FloatField(null=True, blank=True)
    updatedAt = models.FloatField(null=True, blank=True)
    closedByUserName = models.CharField(max_length=255, default="")
    closedAt = models.FloatField(null=True, blank=True)
    assigneeUserName = models.CharField(max_length=255, default="")
    disabled = models.BooleanField(default=False)
    url = models.TextField()
    labels = models.TextField(default="[]")  # ???json ??????????????????label, ????????????label??????????????????????????????
    is_bug = models.BooleanField(default=False)

    user_assignee = models.ForeignKey(
        "ums.User",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="+",
    )
    user_authored = models.ForeignKey(
        "ums.User",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="+",
    )
    user_closed = models.ForeignKey(
        "ums.User",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="+",
    )

    class Meta:
        indexes = [
            models.Index(fields=["authoredByUserName"]),
            models.Index(fields=["closedByUserName"]),
            models.Index(fields=["repo"]),
        ]


class CommitSRAssociation(models.Model):
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)
    auto_added = models.BooleanField(models.BooleanField, default=False)

    class Meta:
        unique_together = ["commit", "SR"]


class MRSRAssociation(models.Model):
    MR = models.ForeignKey(MergeRequest, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)
    auto_added = models.BooleanField(models.BooleanField, default=False)

    class Meta:
        unique_together = ["MR", "SR"]


class IssueSRAssociation(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    SR = models.ForeignKey("rms.SR", on_delete=models.CASCADE)
    auto_added = models.BooleanField(models.BooleanField, default=False)

    class Meta:
        unique_together = ["issue", "SR"]


class IssueMRAssociation(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    MR = models.ForeignKey(MergeRequest, on_delete=models.CASCADE)
    auto_added = models.BooleanField(models.BooleanField, default=False)

    class Meta:
        unique_together = ["issue", "MR"]


class RemoteRepo(models.Model):
    """
    ????????????????????????
    """

    id = models.BigAutoField(primary_key=True)
    type = models.CharField(
        max_length=50
    )  # ??????????????????????????????query_class.py ?????????????????????????????? ???????????????????????? 'gitlab'
    remote_id = models.TextField(default="")  # ????????????id???????????????String
    access_token = models.TextField(default="")
    enable_crawling = models.BooleanField(default=True)  # ??????????????????
    info = models.TextField(default="{}")  # ????????????????????????
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)  # ?????????????????????
    secret_token = models.CharField(max_length=255, default="", unique=True)
    created = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["repo"]), models.Index(fields=["secret_token"])]


class CrawlLog(models.Model):
    """
    ??????????????? **????????????webhook**
    """

    id = models.BigAutoField(primary_key=True)
    repo = models.ForeignKey(RemoteRepo, on_delete=models.CASCADE)  # ??????????????????
    time = models.FloatField()  # ????????????
    status = models.IntegerField(default=200)  # ?????????HTTP??????
    message = models.TextField(default="")  # ????????????
    request_type = models.TextField(
        default="general"
    )  # ??????????????????commit, merge, issue; general??????????????????????????????
    finished = models.BooleanField(default=False)  # ?????????????????????False ?????????????????????????????????????????????
    updated = models.BooleanField(
        default=False
    )  # ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
    is_webhook = models.BooleanField(default=False)


class CrawlerOp(models.TextChoices):
    """
    operation ???????????????commit?????????
        insert: ???????????????????????????????????????commit???????????????????????????
        update: ???????????????????????????????????????commit???????????????????????????????????????
        remove??? ???????????????????????????????????????commit????????????????????????????????????
    """

    UPDATE = "update"
    INSERT = "insert"
    REMOVE = "remove"


class CommitCrawlAssociation(models.Model):
    """
    ???????????????Commit?????????????????????
    """

    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)


class MergeCrawlAssociation(models.Model):
    """
    ???????????????MR?????????????????????
    """

    merge = models.ForeignKey(MergeRequest, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)


class IssueCrawlAssociation(models.Model):
    """
    ???????????????Issue?????????????????????
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)


class PendingWebhookRequests(models.Model):
    remote = models.ForeignKey(RemoteRepo, on_delete=models.CASCADE)
    body = models.TextField()

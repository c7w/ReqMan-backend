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
    commiter_name = models.CharField(max_length=255)
    createdAt = models.FloatField()
    url = models.TextField()
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["commiter_email"]),
            models.Index(fields=["commiter_name"]),
        ]


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

    class Meta:
        indexes = [
            models.Index(fields=["authoredByUserName"]),
            models.Index(fields=["reviewedByUserName"]),
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
    authoredByUserName = models.CharField(max_length=255)
    authoredAt = models.FloatField(null=True, blank=True)
    updatedAt = models.FloatField(null=True, blank=True)
    closedByUserName = models.CharField(max_length=255)
    closedAt = models.FloatField(null=True, blank=True)
    assigneeUserName = models.CharField(max_length=255)
    disabled = models.BooleanField(default=False)
    url = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["authoredByUserName"]),
            models.Index(fields=["closedByUserName"]),
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
    """
    记录远程仓库信息
    """

    id = models.BigAutoField(primary_key=True)
    type = models.CharField(
        max_length=50
    )  # 远程仓库类型，用于在query_class.py 中匹配相应的请求类， 目前支持的字符串 'gitlab'
    remote_id = models.TextField()  # 远程仓库id，有意设为String
    access_token = models.TextField()
    enable_crawling = models.BooleanField(default=True)  # 是否同步仓库
    info = models.TextField(default="{}")  # 额外信息，如网址
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)  # 对应的本地仓库

    class Meta:
        indexes = [
            models.Index(fields=["repo"]),
        ]


class CrawlLog(models.Model):
    """
    记录每一次
    """

    id = models.BigAutoField(primary_key=True)
    repo = models.ForeignKey(RemoteRepo, on_delete=models.CASCADE)  # 对应远程仓库
    time = models.FloatField()  # 爬取时间
    status = models.IntegerField(default=200)  # 爬取的HTTP状态
    message = models.TextField(default="")  # 错误信息
    request_type = models.TextField(
        default="general"
    )  # 爬取的类型：commit, merge, issue; general为还没爬就报错时使用
    finished = models.BooleanField(default=False)  # 是否成功结束：False 表示处理过程中出错，没有处理完
    updated = models.BooleanField(
        default=False
    )  # 本次爬取是否对数据库做了修改，加上是考虑到大部分爬取都没有修改，用这个字段可以加速查询速度


class CrawlerOp(models.TextChoices):
    """
    operation 的含义，以commit为例：
        insert: 这次爬取发现远程新增了一个commit，本题同步增加一个
        update: 这次爬取发现远程修改了一个commit，本地的相应记录也同步修改
        remove： 这次爬取发现远程删除了一个commit，本地的相应记录标为删除
    """

    UPDATE = "update"
    INSERT = "insert"
    REMOVE = "remove"


class CommitCrawlAssociation(models.Model):
    """
    记录爬取和Commit更新之间的关系
    """

    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)


class MergeCrawlAssociation(models.Model):
    """
    记录爬取和MR更新之间的关系
    """

    merge = models.ForeignKey(MergeRequest, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)


class IssueCrawlAssociation(models.Model):
    """
    记录爬取和Issue更新之间的关系
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    crawl = models.ForeignKey(CrawlLog, on_delete=models.CASCADE)
    operation = models.CharField(max_length=10)

import datetime as dt
from pyexpat import model
import pytz
from backend.settings import TIME_ZONE
from django.db import models
import utils.model_date as getTime

# Create your models here.


class Iteration(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    sid = models.IntegerField()
    title = models.CharField(max_length=255)
    begin = models.FloatField()
    end = models.FloatField()
    disabled = models.BooleanField(default=False)
    createAt = models.FloatField(default=getTime.get_timestamp)

    class Meta:
        indexes = [models.Index(fields=["project"])]


class UserIterationAssociation(models.Model):
    user = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["iteration"]),
            models.Index(fields=["user", "iteration"]),
        ]
        unique_together = ["user", "iteration"]


class IR(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    rank = models.IntegerField()
    createdBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["title"]),
            models.Index(fields=["title", "project"]),
        ]
        unique_together = ["project", "title"]


class SR(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.IntegerField()
    rank = models.IntegerField()
    IR = models.ManyToManyField(
        IR,
        through="IRSRAssociation",
    )

    class SRState(models.TextChoices):
        TODO = "TODO"
        WIP = "WIP"
        Reviewing = "Reviewing"
        Done = "Done"

    state = models.TextField(choices=SRState.choices)
    createdBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["title"]),
            models.Index(fields=["title", "project"]),
        ]
        unique_together = ["project", "title"]


class IRSRAssociation(models.Model):
    IR = models.ForeignKey(IR, on_delete=models.CASCADE)
    SR = models.ForeignKey(SR, on_delete=models.CASCADE)


class SRIterationAssociation(models.Model):
    SR = models.ForeignKey(SR, on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE)


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    rank = models.IntegerField()
    createdBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    createdAt = models.FloatField(default=getTime.get_timestamp)
    disabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["title"]),
            models.Index(fields=["title", "project"]),
        ]
        unique_together = ["project", "title"]


class SR_Changelog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    project = models.ForeignKey("ums.Project", on_delete=models.CASCADE)
    SR = models.ForeignKey(SR, on_delete=models.CASCADE)
    description = models.TextField()

    class SRState(models.TextChoices):
        TODO = "TODO"
        WIP = "WIP"
        Done = "Done"

    formerState = models.TextField(choices=SRState.choices)
    formerDescription = models.TextField()
    changedBy = models.ForeignKey("ums.User", on_delete=models.CASCADE)
    changedAt = models.FloatField(default=getTime.get_timestamp)


class ServiceSRAssociation(models.Model):
    SR = models.ForeignKey(SR, on_delete=models.CASCADE, unique=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

class IRIterationAssociation(models.Model):
    IR = models.ForeignKey(IR,on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration,on_delete=models.CASCADE)

    class Meta:
        unique_together = ("IR","iteration")

class ProjectIterationAssociation(models.Model):
    project = models.ForeignKey("ums.Project",on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration,on_delete=models.CASCADE)

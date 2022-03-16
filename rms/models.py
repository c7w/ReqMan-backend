from faulthandler import disable
from operator import index
from venv import create
from django.db import models

# Create your models here.

class Iteration(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey('ums.Project',on_delete=models.CASCADE)
    sid = models.IntegerField()
    title = models.TextField()
    begin = models.FloatField()
    end = models.FloatField()
    disabled = models.BooleanField()
    createAt = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['project'])
        ]


class UserIterationAssociation(models.Model):
    user = models.ForeignKey('ums.User',on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration,on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['iteration']),
        ]
        unique_together = ('user','iteration')


class IR(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey('ums.Project',on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    rank = models.IntegerField()
    createdBy = models.ForeignKey('ums.User',on_delete=models.CASCADE)
    createdAt = models.FloatField()
    disabled = models.BooleanField()

    class Meta:
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['title'])
        ]
        unique_together = ('project','title')

class SR(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey('ums.Project',on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    priority = models.IntegerField()
    rank = models.IntegerField()

    class SRState(models.TextChoices):
        TODO = 'TODO'
        WIP = 'WIP'
        Reviewing = 'Reviewing'
        Done = 'Done'
    
    state = models.TextField(choices=SRState.choices)
    createdBy = models.ForeignKey('ums.User',on_delete=models.CASCADE)
    createdAt = models.FloatField()
    disabled = models.BooleanField()

    class Meta:
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['title'])
        ]
        unique_together = ('project','title')

class IRSRAssociation(models.Model):
    IR = models.ForeignKey(IR,on_delete=models.CASCADE)
    SR = models.ForeignKey(SR,on_delete=models.CASCADE)

class SRIterationAssociation(models.Model):
    SR = models.ForeignKey(SR,on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration,on_delete=models.CASCADE)

class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey('ums.Project',on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    rank = models.IntegerField()
    createdBy = models.ForeignKey('ums.User',on_delete=models.CASCADE)
    createdAt = models.FloatField()
    disabled = models.BooleanField()

    class Meta:
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['title'])
        ]
        unique_together = ('project','title')

class SR_Changelog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    project = models.ForeignKey('ums.Project',on_delete=models.CASCADE)
    SR = models.ForeignKey(SR,on_delete=models.CASCADE)
    description = models.TextField()
    
    class SRState(models.TextChoices):
        TODO = 'TODO'
        WIP = 'WIP'
        Done = 'Done'
    
    formerState = models.TextField(choices=SRState.choices)
    formerDescription = models.TextField()
    changedBy = models.ForeignKey('ums.User',on_delete=models.CASCADE)
    changedAt = models.FloatField()

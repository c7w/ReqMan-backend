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

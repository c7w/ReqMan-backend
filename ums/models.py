from django.db import models

# Create your models here.

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(unique=True)
    password = models.TextField()
    email = models.TextField()
    avatar = models.TextField()
    disabled = models.BooleanField(default=False)
    createAt = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

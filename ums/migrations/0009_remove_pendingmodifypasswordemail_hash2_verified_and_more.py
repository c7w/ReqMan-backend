# Generated by Django 4.0.3 on 2022-03-31 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "ums",
            "0008_rename_verified_pendingmodifypasswordemail_hash1_verified_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pendingmodifypasswordemail",
            name="hash2_verified",
        ),
        migrations.AddField(
            model_name="pendingmodifypasswordemail",
            name="beginAt",
            field=models.FloatField(default=-1),
        ),
        migrations.AlterField(
            model_name="pendingmodifypasswordemail",
            name="hash2",
            field=models.CharField(default="", max_length=100, unique=True),
        ),
    ]

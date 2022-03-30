# Generated by Django 4.0.3 on 2022-03-24 16:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0002_alter_project_createdat_alter_sessionpool_expireat_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="createdAt",
            field=models.FloatField(default=1648138466.577152),
        ),
        migrations.AlterField(
            model_name="sessionpool",
            name="expireAt",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 3, 27, 16, 14, 26, 577152, tzinfo=utc)
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="createdAt",
            field=models.FloatField(default=1648138466.577152),
        ),
    ]

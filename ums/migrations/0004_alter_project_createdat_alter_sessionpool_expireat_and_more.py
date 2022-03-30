# Generated by Django 4.0.3 on 2022-03-24 16:15

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0003_alter_project_createdat_alter_sessionpool_expireat_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="createdAt",
            field=models.FloatField(default=1648138502.235897),
        ),
        migrations.AlterField(
            model_name="sessionpool",
            name="expireAt",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 3, 27, 16, 15, 2, 235897, tzinfo=utc)
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="createdAt",
            field=models.FloatField(default=1648138502.235897),
        ),
    ]

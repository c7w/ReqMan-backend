# Generated by Django 4.0.3 on 2022-03-27 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0002_alter_project_createdat_alter_sessionpool_expireat_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="avatar",
            field=models.TextField(default=""),
        ),
    ]

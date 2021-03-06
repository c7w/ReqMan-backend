# Generated by Django 4.0.3 on 2022-03-26 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rdts", "0002_alter_repository_createdat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="assigneeUserName",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="issue",
            name="authoredByUserName",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="issue",
            name="closedByUserName",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddIndex(
            model_name="commit",
            index=models.Index(fields=["repo"], name="rdts_commit_repo_id_330aeb_idx"),
        ),
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["repo"], name="rdts_issue_repo_id_c8f154_idx"),
        ),
        migrations.AddIndex(
            model_name="mergerequest",
            index=models.Index(fields=["repo"], name="rdts_merger_repo_id_9fd5e8_idx"),
        ),
    ]

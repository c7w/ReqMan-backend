# Generated by Django 4.0.3 on 2022-04-14 01:37

from django.db import migrations, models
import django.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("rdts", "0011_commit_additions_commit_deletions_commit_diff"),
    ]

    operations = [
        migrations.AddField(
            model_name="commitsrassociation",
            name="auto_added",
            field=models.BooleanField(
                default=False, verbose_name=django.db.models.fields.BooleanField
            ),
        ),
        migrations.AddField(
            model_name="issuemrassociation",
            name="auto_added",
            field=models.BooleanField(
                default=False, verbose_name=django.db.models.fields.BooleanField
            ),
        ),
        migrations.AddField(
            model_name="issuesrassociation",
            name="auto_added",
            field=models.BooleanField(
                default=False, verbose_name=django.db.models.fields.BooleanField
            ),
        ),
        migrations.AddField(
            model_name="mrsrassociation",
            name="auto_added",
            field=models.BooleanField(
                default=False, verbose_name=django.db.models.fields.BooleanField
            ),
        ),
    ]

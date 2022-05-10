# Generated by Django 4.0.3 on 2022-05-10 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0017_remove_project_local_sr_title_pattern_extract"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectinvitationassociation",
            name="role",
            field=models.CharField(
                choices=[
                    ("member", "Member"),
                    ("dev", "Dev"),
                    ("qa", "Qa"),
                    ("sys", "Sys"),
                    ("supermaster", "Supermaster"),
                ],
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="userprojectassociation",
            name="role",
            field=models.CharField(
                choices=[
                    ("member", "Member"),
                    ("dev", "Dev"),
                    ("qa", "Qa"),
                    ("sys", "Sys"),
                    ("supermaster", "Supermaster"),
                ],
                max_length=12,
            ),
        ),
    ]
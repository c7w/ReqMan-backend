# Generated by Django 4.0.3 on 2022-03-26 04:08

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("disabled", models.BooleanField(default=False)),
                ("createdAt", models.FloatField(default=1648267711.021621)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("password", models.TextField()),
                ("email", models.CharField(max_length=255, unique=True)),
                ("avatar", models.TextField(default="")),
                ("disabled", models.BooleanField(default=False)),
                ("createdAt", models.FloatField(default=1648267711.022101)),
            ],
        ),
        migrations.CreateModel(
            name="UserProjectAssociation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.TextField(
                        choices=[
                            ("member", "Member"),
                            ("dev", "Dev"),
                            ("qa", "Qa"),
                            ("sys", "Sys"),
                            ("supermaster", "Supermaster"),
                        ]
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.project"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="project",
            field=models.ManyToManyField(
                through="ums.UserProjectAssociation", to="ums.project"
            ),
        ),
        migrations.CreateModel(
            name="SessionPool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sessionId", models.CharField(max_length=32)),
                (
                    "expireAt",
                    models.DateTimeField(
                        default=datetime.datetime(2022, 3, 28, 12, 8, 31, 22504)
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProjectInvitationAssociation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("invitation", models.CharField(max_length=64)),
                (
                    "role",
                    models.TextField(
                        choices=[
                            ("member", "Member"),
                            ("dev", "Dev"),
                            ("qa", "Qa"),
                            ("sys", "Sys"),
                            ("supermaster", "Supermaster"),
                        ]
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.project"
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["title"], name="ums_project_title_e5c6c7_idx"),
        ),
        migrations.AddIndex(
            model_name="userprojectassociation",
            index=models.Index(
                fields=["project"], name="ums_userpro_project_fc58aa_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userprojectassociation",
            index=models.Index(fields=["user"], name="ums_userpro_user_id_791d13_idx"),
        ),
        migrations.AddIndex(
            model_name="userprojectassociation",
            index=models.Index(
                fields=["user", "project"], name="ums_userpro_user_id_941570_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="userprojectassociation",
            unique_together={("user", "project")},
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["name"], name="ums_user_name_cf444d_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="ums_user_email_83a62c_idx"),
        ),
        migrations.AddIndex(
            model_name="projectinvitationassociation",
            index=models.Index(
                fields=["project"], name="ums_project_project_b45d35_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="projectinvitationassociation",
            index=models.Index(
                fields=["invitation"], name="ums_project_invitat_f78208_idx"
            ),
        ),
    ]

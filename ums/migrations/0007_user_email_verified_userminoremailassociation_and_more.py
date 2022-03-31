# Generated by Django 4.0.3 on 2022-03-31 04:09

from django.db import migrations, models
import django.db.models.deletion
import utils.model_date


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0006_alter_project_createdat_alter_sessionpool_expireat_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="UserMinorEmailAssociation",
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
                ("email", models.TextField()),
                ("verified", models.BooleanField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PendingModifyPasswordEmail",
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
                ("email", models.TextField()),
                ("hash1", models.CharField(max_length=100, unique=True)),
                ("hash2", models.CharField(max_length=100, unique=True)),
                (
                    "createdAt",
                    models.FloatField(default=utils.model_date.get_timestamp),
                ),
                ("verified", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="userminoremailassociation",
            index=models.Index(fields=["user"], name="ums_usermin_user_id_9d8032_idx"),
        ),
        migrations.AddIndex(
            model_name="userminoremailassociation",
            index=models.Index(fields=["email"], name="ums_usermin_email_ab3fb8_idx"),
        ),
        migrations.AddIndex(
            model_name="pendingmodifypasswordemail",
            index=models.Index(fields=["hash1"], name="ums_pending_hash1_62ae72_idx"),
        ),
        migrations.AddIndex(
            model_name="pendingmodifypasswordemail",
            index=models.Index(fields=["hash2"], name="ums_pending_hash2_21388f_idx"),
        ),
    ]

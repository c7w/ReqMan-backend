# Generated by Django 4.0.3 on 2022-03-26 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("ums", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="IR",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("rank", models.IntegerField()),
                ("createdAt", models.FloatField(default=1648267711.016193)),
                ("disabled", models.BooleanField(default=False)),
                (
                    "createdBy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
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
        migrations.CreateModel(
            name="IRSRAssociation",
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
                    "IR",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rms.ir"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Iteration",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("sid", models.IntegerField()),
                ("title", models.CharField(max_length=255)),
                ("begin", models.FloatField()),
                ("end", models.FloatField()),
                ("disabled", models.BooleanField(default=False)),
                ("createAt", models.FloatField(default=1648267711.015049)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.project"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SR",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("priority", models.IntegerField()),
                ("rank", models.IntegerField()),
                (
                    "state",
                    models.TextField(
                        choices=[
                            ("TODO", "Todo"),
                            ("WIP", "Wip"),
                            ("Reviewing", "Reviewing"),
                            ("Done", "Done"),
                        ]
                    ),
                ),
                ("createdAt", models.FloatField(default=1648267711.016804)),
                ("disabled", models.BooleanField(default=False)),
                (
                    "IR",
                    models.ManyToManyField(through="rms.IRSRAssociation", to="rms.ir"),
                ),
                (
                    "createdBy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
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
        migrations.CreateModel(
            name="UserIterationAssociation",
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
                    "iteration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rms.iteration"
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
            name="SRIterationAssociation",
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
                    "SR",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rms.sr"
                    ),
                ),
                (
                    "iteration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rms.iteration"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SR_Changelog",
            fields=[
                ("id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("description", models.TextField()),
                (
                    "formerState",
                    models.TextField(
                        choices=[("TODO", "Todo"), ("WIP", "Wip"), ("Done", "Done")]
                    ),
                ),
                ("formerDescription", models.TextField()),
                ("changedAt", models.FloatField(default=1648267711.018432)),
                (
                    "SR",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rms.sr"
                    ),
                ),
                (
                    "changedBy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
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
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("rank", models.IntegerField()),
                ("createdAt", models.FloatField(default=1648267711.017859)),
                ("disabled", models.BooleanField(default=False)),
                (
                    "createdBy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ums.user"
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
        migrations.AddField(
            model_name="irsrassociation",
            name="SR",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="rms.sr"
            ),
        ),
        migrations.AddIndex(
            model_name="useriterationassociation",
            index=models.Index(fields=["user"], name="rms_userite_user_id_c34710_idx"),
        ),
        migrations.AddIndex(
            model_name="useriterationassociation",
            index=models.Index(
                fields=["iteration"], name="rms_userite_iterati_9592cc_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="useriterationassociation",
            index=models.Index(
                fields=["user", "iteration"], name="rms_userite_user_id_30c74e_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="useriterationassociation",
            unique_together={("user", "iteration")},
        ),
        migrations.AddIndex(
            model_name="sr",
            index=models.Index(fields=["project"], name="rms_sr_project_9cbd11_idx"),
        ),
        migrations.AddIndex(
            model_name="sr",
            index=models.Index(fields=["title"], name="rms_sr_title_893bbf_idx"),
        ),
        migrations.AddIndex(
            model_name="sr",
            index=models.Index(
                fields=["title", "project"], name="rms_sr_title_72d64e_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sr",
            unique_together={("project", "title")},
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(
                fields=["project"], name="rms_service_project_55e4c2_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(fields=["title"], name="rms_service_title_7fe83d_idx"),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(
                fields=["title", "project"], name="rms_service_title_0791c9_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="service",
            unique_together={("project", "title")},
        ),
        migrations.AddIndex(
            model_name="iteration",
            index=models.Index(
                fields=["project"], name="rms_iterati_project_4bbbb8_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="ir",
            index=models.Index(fields=["project"], name="rms_ir_project_3d4987_idx"),
        ),
        migrations.AddIndex(
            model_name="ir",
            index=models.Index(fields=["title"], name="rms_ir_title_e02679_idx"),
        ),
        migrations.AddIndex(
            model_name="ir",
            index=models.Index(
                fields=["title", "project"], name="rms_ir_title_0bba6a_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ir",
            unique_together={("project", "title")},
        ),
    ]

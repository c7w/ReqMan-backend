# Generated by Django 4.0.3 on 2022-05-13 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rdts", "0019_remove_commit_rdts_commit_commite_d20353_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="remoterepo",
            name="created",
            field=models.BooleanField(default=False),
        ),
    ]
# Generated by Django 4.0.3 on 2022-05-13 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rdts", "0020_remoterepo_created"),
    ]

    operations = [
        migrations.AddField(
            model_name="mergerequest",
            name="updated_at",
            field=models.FloatField(default=0, null=True),
        ),
    ]

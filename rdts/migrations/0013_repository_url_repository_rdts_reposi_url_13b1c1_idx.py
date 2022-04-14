# Generated by Django 4.0.3 on 2022-04-14 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rdts", "0012_commitsrassociation_auto_added_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="url",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="repository",
            index=models.Index(fields=["url"], name="rdts_reposi_url_13b1c1_idx"),
        ),
    ]

# Generated by Django 4.0.3 on 2022-03-31 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0009_remove_pendingmodifypasswordemail_hash2_verified_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userminoremailassociation",
            name="verified",
            field=models.BooleanField(default=False),
        ),
    ]

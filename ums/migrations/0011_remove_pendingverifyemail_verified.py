# Generated by Django 4.0.3 on 2022-03-31 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0010_alter_userminoremailassociation_verified"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pendingverifyemail",
            name="verified",
        ),
    ]

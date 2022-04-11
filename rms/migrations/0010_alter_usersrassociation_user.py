# Generated by Django 4.0.3 on 2022-04-05 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ums", "0011_remove_pendingverifyemail_verified"),
        ("rms", "0009_usersrassociation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usersrassociation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ums.user"
            ),
        ),
    ]

# Generated by Django 4.0.3 on 2022-04-05 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rms', '0010_alter_usersrassociation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sr_changelog',
            name='formerState',
            field=models.TextField(choices=[('TODO', 'Todo'), ('WIP', 'Wip'), ('Done', 'Done'), ('Reviewing', 'Reviewing')]),
        ),
    ]

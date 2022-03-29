# Generated by Django 4.0.3 on 2022-03-29 02:25

from django.db import migrations, models
import utils.model_date


class Migration(migrations.Migration):

    dependencies = [
        ('ums', '0005_merge_20220329_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='createdAt',
            field=models.FloatField(default=utils.model_date.get_timestamp),
        ),
        migrations.AlterField(
            model_name='sessionpool',
            name='expireAt',
            field=models.DateTimeField(default=utils.model_date.get_datetime),
        ),
        migrations.AlterField(
            model_name='user',
            name='createdAt',
            field=models.FloatField(default=utils.model_date.get_timestamp),
        ),
    ]

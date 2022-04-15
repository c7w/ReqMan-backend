# Generated by Django 4.0.3 on 2022-04-14 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rdts', '0013_repository_url_repository_rdts_reposi_url_13b1c1_idx'),
        ('ums', '0014_config_config_ums_config_key_84db69_idx'),
        ('rms', '0012_sr_pattern_sr_rms_sr_pattern_708bb8_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='sr_changelog',
            name='autoAddCrawl',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='rdts.crawllog'),
        ),
        migrations.AddField(
            model_name='sr_changelog',
            name='autoAdded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sr_changelog',
            name='autoAddedTriggerType',
            field=models.CharField(default='', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='sr_changelog',
            name='autoAddedTriggerValue',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='sr_changelog',
            name='changedBy',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ums.user'),
        ),
        migrations.AlterField(
            model_name='sr_changelog',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
# Generated by Django 3.2.12 on 2022-03-07 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='mturk_hit_expiration',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='mturk_hit_id',
            field=models.CharField(editable=False, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='mturk_hit_status',
            field=models.CharField(editable=False, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='mturk_hit_title',
            field=models.CharField(editable=False, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='mturk_batch_id',
            field=models.PositiveIntegerField(editable=False, null=True),
        ),
    ]

# Generated by Django 3.2.12 on 2022-03-01 01:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_alter_audit_submission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='submission',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='task.submission'),
        ),
    ]

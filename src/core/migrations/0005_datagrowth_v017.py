# Generated by Django 3.2 on 2021-05-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_on_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collective',
            name='schema',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='schema',
        ),
        migrations.AlterField(
            model_name='httpresourcemock',
            name='head',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='httpresourcemock',
            name='request',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='properties',
            field=models.JSONField(default=dict),
        ),
    ]

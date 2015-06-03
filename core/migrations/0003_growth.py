# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_collective_individual'),
    ]

    operations = [
        migrations.CreateModel(
            name='Growth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
                ('input', models.CharField(max_length=255)),
                ('config', core.utils.configuration.ConfigurationField(default={})),
                ('process', models.CharField(max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources')])),
                ('success', models.CharField(max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources')])),
                ('output', models.CharField(max_length=255)),
                ('task_id', models.CharField(max_length=255, null=True, blank=True)),
                ('state', models.CharField(default='New', max_length=255, choices=[(b'RETRY', 'Retry'), (b'ERROR', 'Error'), (b'NEW', 'New'), (b'PROCESSING', 'Processing'), (b'FINISHED', 'Finished')])),
                ('is_finished', models.BooleanField(default=False)),
            ],
        ),
    ]

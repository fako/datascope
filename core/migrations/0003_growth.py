# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0002_collective_individual'),
    ]

    operations = [
        migrations.CreateModel(
            name='Growth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
                ('config', core.utils.configuration.ConfigurationField(default={})),
                ('process', models.CharField(max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources')])),
                ('contribute', models.CharField(max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources')])),
                ('contribute_type', models.CharField(max_length=255, choices=[(b'APPEND', 'Append')])),
                ('input_id', models.PositiveIntegerField(null=True)),
                ('output_id', models.PositiveIntegerField()),
                ('result_id', models.CharField(max_length=255, null=True, blank=True)),
                ('state', models.CharField(default='New', max_length=255, db_index=True, choices=[(b'RETRY', 'Retry'), (b'PARTIAL', 'Partial'), (b'ERROR', 'Error'), (b'NEW', 'New'), (b'PROCESSING', 'Processing'), (b'FINISHED', 'Finished')])),
                ('is_finished', models.BooleanField(default=False, db_index=True)),
                ('input_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType', null=True)),
                ('output_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0012_auto_20160228_2019'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageFeatures',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('uri', models.CharField(db_index=True, max_length=255, default=None)),
                ('data_hash', models.CharField(db_index=True, max_length=255, default='')),
                ('config', core.utils.configuration.ConfigurationField()),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('retainer_type', models.ForeignKey(null=True, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

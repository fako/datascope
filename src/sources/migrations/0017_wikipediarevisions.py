# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0016_wikipediatransclusions'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikipediaRevisions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('uri', models.CharField(default=None, max_length=255, db_index=True)),
                ('data_hash', models.CharField(default='', max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'Wikipedia revisions',
                'verbose_name_plural': 'Wikipedia revisions',
            },
        ),
    ]

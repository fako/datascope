# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field as jsonfield
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0005_wikipediatranslate'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(default=None, max_length=255, db_index=True)),
                ('data_hash', models.CharField(default='', max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField(default={})),
                ('request', jsonfield.fields.JSONField(default=None)),
                ('head', jsonfield.fields.JSONField(default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0018_wikipediaedit_wikipedialogin_wikipediatoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficialAnnouncementsDocumentNetherlands',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uri', models.CharField(db_index=True, default=None, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('data_hash', models.CharField(db_index=True, default='', max_length=255)),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name_plural': 'Official announcements document (Dutch)',
                'verbose_name': 'Official announcements document (Dutch)',
            },
        ),
        migrations.CreateModel(
            name='OfficialAnnouncementsNetherlands',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uri', models.CharField(db_index=True, default=None, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('data_hash', models.CharField(db_index=True, default='', max_length=255)),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name_plural': 'Official announcements (Dutch)',
                'verbose_name': 'Official announcements (Dutch)',
            },
        ),
    ]

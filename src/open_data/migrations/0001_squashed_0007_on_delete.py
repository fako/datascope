# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-21 12:51
from __future__ import unicode_literals

import core.processors.mixins
import datagrowth.configuration.fields
from django.db import migrations, models
import django.db.models.deletion
import json_field.fields


class Migration(migrations.Migration):

    replaces = [('open_data', '0001_initial'), ('open_data', '0002_auto_20170320_1518'), ('open_data', '0003_officialannouncementsdocumentnetherlands_officialannouncementsnetherlands'), ('open_data', '0004_auto_20181202_1424'), ('open_data', '0005_auto_20190402_0928'), ('open_data', '0006_alter_data_hash'), ('open_data', '0007_on_delete')]

    initial = True

    dependencies = [
        ('core', '0017_auto_20170315_1639'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DutchParliamentarySeatingTranscriptsCommunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(db_index=True, max_length=255)),
                ('config', datagrowth.configuration.fields.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('state', models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Retry', 'Retry'), ('Synchronous', 'Synchronous')], default='New', max_length=255)),
                ('current_growth', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Growth')),
                ('kernel_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Dutch parliamentary seating transcripts',
                'verbose_name': 'Dutch parliamentary seating transcripts',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
        migrations.CreateModel(
            name='OfficialAnnouncementsDocumentNetherlands',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(db_index=True, default=None, max_length=255)),
                ('status', models.PositiveIntegerField(default=0)),
                ('config', datagrowth.configuration.fields.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(blank=True, null=True)),
                ('data_hash', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('request', json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object')),
                ('head', json_field.fields.JSONField(default='{}', help_text='Enter a valid JSON object')),
                ('body', models.TextField(blank=True, default=None, null=True)),
                ('retainer_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Official announcements document (Dutch)',
                'verbose_name_plural': 'Official announcements document (Dutch)',
            },
        ),
        migrations.CreateModel(
            name='OfficialAnnouncementsNetherlands',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(db_index=True, default=None, max_length=255)),
                ('status', models.PositiveIntegerField(default=0)),
                ('config', datagrowth.configuration.fields.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(blank=True, null=True)),
                ('data_hash', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('request', json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object')),
                ('head', json_field.fields.JSONField(default='{}', help_text='Enter a valid JSON object')),
                ('body', models.TextField(blank=True, default=None, null=True)),
                ('retainer_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Official announcements (Dutch)',
                'verbose_name_plural': 'Official announcements (Dutch)',
            },
        ),
    ]

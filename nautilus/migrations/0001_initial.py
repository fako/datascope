# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.models.organisms.mixins
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20170315_1639'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocaforaLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=255, db_index=True, default=None)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('data_hash', models.CharField(max_length=255, db_index=True, default='')),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocaforaOrderOverviewCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(max_length=255, choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], default='New')),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(null=True, blank=True, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Locafora order overview community',
                'verbose_name_plural': 'Locafora order overview communities',
            },
            bases=(models.Model, core.models.organisms.mixins.ProcessorMixin),
        ),
        migrations.CreateModel(
            name='LocaforaOrders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=255, db_index=True, default=None)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('retainer_id', models.PositiveIntegerField(null=True)),
                ('data_hash', models.CharField(max_length=255, db_index=True, default='')),
                ('request', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('head', json_field.fields.JSONField(help_text='Enter a valid JSON object', default=None)),
                ('body', models.TextField(default=None)),
                ('status', models.PositiveIntegerField(default=None)),
                ('retainer_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'Locafora order',
                'verbose_name_plural': 'Locafora orders',
            },
        ),
    ]

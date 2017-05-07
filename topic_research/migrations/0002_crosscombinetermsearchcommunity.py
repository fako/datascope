# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models.organisms.mixins
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0017_auto_20170315_1639'),
        ('topic_research', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrossCombineTermSearchCommunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('purge_at', models.DateTimeField(blank=True, null=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(default='New', max_length=255, choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')])),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'created_at',
            },
            bases=(models.Model, core.models.organisms.mixins.ProcessorMixin),
        ),
    ]

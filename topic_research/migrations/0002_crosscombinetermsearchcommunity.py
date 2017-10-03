# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.processors.mixins


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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(default='New', max_length=255, choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')])),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'verbose_name': 'Cross combine search term community',
                'verbose_name_plural': 'Cross combine search term communities',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.models.organisms.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160627_2118'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikipediaCategorySimularityCommunity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('signature', models.CharField(db_index=True, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], max_length=255, default='New')),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
            bases=(models.Model, core.models.organisms.mixins.ProcessorMixin),
        ),
    ]

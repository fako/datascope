# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.processors.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160627_2118'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikipediaCategorySimularityCommunity',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(max_length=255, choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], default='New')),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Wikipedia categories similarities',
                'verbose_name': 'Wikipedia category similarity',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.processors.mixins
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0014_auto_20160226_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='FutureFashionCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(max_length=255, default='New', choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')])),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'verbose_name': 'Future fashion',
                'verbose_name_plural': 'Future fashions',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.models.organisms.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160627_2118'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wiki_feed', '0002_auto_20170201_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiFeedUsageCommunity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('signature', models.CharField(db_index=True, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(default='New', choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], max_length=255)),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(to='contenttypes.ContentType', blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Wiki feed usages',
                'verbose_name': 'Wiki feed usage',
            },
            bases=(models.Model, core.models.organisms.mixins.ProcessorMixin),
        ),
    ]

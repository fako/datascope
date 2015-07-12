# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0004_communitymock'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiNewsCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature', models.CharField(max_length=255, db_index=True)),
                ('config', core.utils.configuration.ConfigurationField(default={})),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(default='New', max_length=255, choices=[(b'NEW', 'New'), (b'READY', 'Ready'), (b'ASYNC', 'Asynchronous'), (b'SYNC', 'Synchronous'), (b'EXPAND', 'Expand')])),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Wiki news',
                'verbose_name_plural': 'Wiki news',
            },
        ),
    ]

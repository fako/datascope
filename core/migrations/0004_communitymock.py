# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0003_growth'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityMock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identity', models.CharField(max_length=255)),
                ('config', core.utils.configuration.ConfigurationField(default={})),
                ('kernel_id', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=1)),
                ('state', models.CharField(max_length=255)),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

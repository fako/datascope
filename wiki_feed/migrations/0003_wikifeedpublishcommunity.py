# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.utils.configuration
import core.processors.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20170315_1639'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wiki_feed', '0002_auto_20170201_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiFeedPublishCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('signature', models.CharField(db_index=True, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(max_length=255, default='New', choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')])),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Wiki feed publication',
                'verbose_name_plural': 'Wiki feed publications',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

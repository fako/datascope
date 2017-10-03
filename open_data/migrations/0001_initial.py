# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.processors.mixins
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0017_auto_20170315_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='DutchParliamentarySeatingTranscriptsCommunity',
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
                ('state', models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], max_length=255, default='New')),
                ('current_growth', models.ForeignKey(null=True, to='core.Growth')),
                ('kernel_type', models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

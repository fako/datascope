# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration
import core.processors.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160226_1306'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('visual_translations', '0004_auto_20160328_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualTranslationsBRICCommunity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('signature', models.CharField(db_index=True, max_length=255)),
                ('config', core.utils.configuration.ConfigurationField()),
                ('kernel_id', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('purge_at', models.DateTimeField(null=True, blank=True)),
                ('views', models.IntegerField(default=0)),
                ('state', models.CharField(default='New', choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], max_length=255)),
                ('current_growth', models.ForeignKey(to='core.Growth', null=True)),
                ('kernel_type', models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Visual translations',
                'verbose_name': 'Visual translation',
            },
            bases=(models.Model, core.processors.mixins.ProcessorMixin),
        ),
    ]

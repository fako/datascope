# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0009_auto_20150828_1945'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manifestation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('community_id', models.PositiveIntegerField()),
                ('uri', models.CharField(default=None, max_length=255, db_index=True)),
                ('data', json_field.fields.JSONField(default='null', help_text='Enter a valid JSON object', null=True)),
                ('task', models.CharField(max_length=255, null=True)),
                ('community_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
        ),
    ]

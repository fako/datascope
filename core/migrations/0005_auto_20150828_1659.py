# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_communitymock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collective',
            name='schema',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='growth',
            name='input_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='growth',
            name='input_type',
            field=models.ForeignKey(related_name='+', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='growth',
            name='output_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='growth',
            name='output_type',
            field=models.ForeignKey(related_name='+', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='httpresourcemock',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='httpresourcemock',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='properties',
            field=json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='schema',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
    ]

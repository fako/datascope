# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-19 13:15
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('topic_research', '0003_webtextresource'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webtextresource',
            name='body',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='webtextresource',
            name='head',
            field=json_field.fields.JSONField(default='{}', help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='webtextresource',
            name='status',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150828_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collective',
            name='groups',
            field=json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', null=True, blank=True),
        ),
    ]

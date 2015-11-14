# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150828_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='collective',
            name='groups',
            field=jsonfield.fields.JSONField(default={}, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='collective',
            name='identifier',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='group_code',
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='identity',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
    ]

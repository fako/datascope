# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0016_auto_20160627_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifestation',
            name='modified_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 15, 16, 39, 32, 564893), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='manifestation',
            name='purge_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='manifestation',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='manifestation',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
    ]

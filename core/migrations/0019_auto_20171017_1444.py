# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-17 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20170910_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifestation',
            name='task',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

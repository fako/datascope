# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-18 18:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topic_research', '0006_auto_20180813_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wikipediacategorysimularitycommunity',
            name='current_growth',
        ),
        migrations.RemoveField(
            model_name='wikipediacategorysimularitycommunity',
            name='kernel_type',
        ),
        migrations.DeleteModel(
            name='WikipediaCategorySimularityCommunity',
        ),
    ]
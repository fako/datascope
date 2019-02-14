# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-02 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki_scope', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wikipediacategorysimilaritycommunity',
            name='views',
        ),
        migrations.AlterField(
            model_name='wikipediacategorysimilaritycommunity',
            name='state',
            field=models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Retry', 'Retry'), ('Synchronous', 'Synchronous')], default='New', max_length=255),
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schema', jsonfield.fields.JSONField(default=None)),
                ('spirit', models.CharField(default=None, max_length=255, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schema', jsonfield.fields.JSONField(default=None)),
                ('spirit', models.CharField(default=None, max_length=255, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('properties', jsonfield.fields.JSONField()),
                ('collective', models.ForeignKey(to='core.Collective', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

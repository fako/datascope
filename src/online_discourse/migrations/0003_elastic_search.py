# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-27 17:41
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('online_discourse', '0002_empty_schema_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElasticIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(max_length=255)),
                ('language', models.CharField(choices=[('en', 'english'), ('nl', 'dutch')], max_length=5)),
                ('configuration', django.contrib.postgres.fields.jsonb.JSONField(blank=True)),
                ('error_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indices', to='online_discourse.DiscourseSearchCommunity')),
            ],
            options={
                'verbose_name': 'elastic index',
                'verbose_name_plural': 'elastic indices',
            },
        ),
    ]

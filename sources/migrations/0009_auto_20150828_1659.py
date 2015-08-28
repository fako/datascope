# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0008_imagedownload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acteursspotprofile',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='acteursspotprofile',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='benfcastingprofile',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='benfcastingprofile',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='googleimage',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='googleimage',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='googletranslate',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='googletranslate',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='imagedownload',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='imagedownload',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='moederannecastingsearch',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='moederannecastingsearch',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='moederannecastingsession',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='moederannecastingsession',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipedialistpages',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipedialistpages',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediarecentchanges',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediarecentchanges',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediasearch',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediasearch',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediatranslate',
            name='head',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
        migrations.AlterField(
            model_name='wikipediatranslate',
            name='request',
            field=json_field.fields.JSONField(default=None, help_text='Enter a valid JSON object'),
        ),
    ]

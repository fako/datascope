# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0009_auto_20150828_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acteursspotprofile',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='benfcastingprofile',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='googleimage',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='googletranslate',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='imagedownload',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='moederannecastingsearch',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='moederannecastingsession',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='wikipedialistpages',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='wikipediarecentchanges',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='wikipediasearch',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='wikipediatranslate',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
    ]

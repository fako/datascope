# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('visual_translations', '0002_auto_20160219_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualtranslationscommunity',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='visualtranslationscommunity',
            name='state',
            field=models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], default='New', max_length=255),
        ),
    ]

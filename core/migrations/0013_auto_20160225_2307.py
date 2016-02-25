# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160219_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitymock',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='communitymock',
            name='state',
            field=models.CharField(choices=[('Aborted', 'Aborted'), ('Asynchronous', 'Asynchronous'), ('New', 'New'), ('Ready', 'Ready'), ('Synchronous', 'Synchronous')], default='New', max_length=255),
        ),
        migrations.AlterField(
            model_name='growth',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='growth',
            name='state',
            field=models.CharField(choices=[('Complete', 'Complete'), ('Contribute', 'Contribute'), ('Error', 'Error'), ('New', 'New'), ('Partial', 'Partial'), ('Processing', 'Processing'), ('Retry', 'Retry')], default='New', db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='httpresourcemock',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
        migrations.AlterField(
            model_name='manifestation',
            name='config',
            field=core.utils.configuration.ConfigurationField(),
        ),
    ]

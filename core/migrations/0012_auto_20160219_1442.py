# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_manifestation_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitymock',
            name='state',
            field=models.CharField(default='New', max_length=255, choices=[('Aborted', 'Aborted'), ('New', 'New'), ('Ready', 'Ready'), ('Asynchronous', 'Asynchronous'), ('Synchronous', 'Synchronous')]),
        ),
    ]

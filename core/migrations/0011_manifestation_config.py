# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils.configuration


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_manifestation'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifestation',
            name='config',
            field=core.utils.configuration.ConfigurationField(default=None),
        ),
    ]

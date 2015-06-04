# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_growth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collective',
            name='spirit',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='spirit',
        ),
    ]

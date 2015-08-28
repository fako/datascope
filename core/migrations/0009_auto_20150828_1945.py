# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150828_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individual',
            old_name='group_code',
            new_name='index',
        ),
    ]

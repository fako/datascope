# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20160622_1528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collective',
            options={'get_latest_by': 'created_at'},
        ),
        migrations.AlterModelOptions(
            name='communitymock',
            options={'get_latest_by': 'created_at'},
        ),
        migrations.AlterModelOptions(
            name='individual',
            options={'get_latest_by': 'created_at'},
        ),
        migrations.AlterModelOptions(
            name='manifestation',
            options={'get_latest_by': 'created_at'},
        ),
    ]

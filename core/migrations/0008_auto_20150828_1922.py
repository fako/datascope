# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150828_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collective',
            old_name='groups',
            new_name='indexes',
        ),
    ]

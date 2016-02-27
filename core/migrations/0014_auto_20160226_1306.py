# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160225_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='growth',
            name='contribute_type',
            field=models.CharField(max_length=255, blank=True, choices=[('Append', 'Append'), ('Inline', 'Inline')], null=True),
        ),
    ]

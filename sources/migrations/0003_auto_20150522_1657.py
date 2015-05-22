# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0002_moederannecastingsearch_moederannecastingsession'),
    ]

    operations = [
        migrations.RenameField(
            model_name='httpresourcemock',
            old_name='post_hash',
            new_name='data_hash',
        ),
        migrations.RenameField(
            model_name='moederannecastingsearch',
            old_name='post_hash',
            new_name='data_hash',
        ),
        migrations.RenameField(
            model_name='moederannecastingsession',
            old_name='post_hash',
            new_name='data_hash',
        ),
    ]

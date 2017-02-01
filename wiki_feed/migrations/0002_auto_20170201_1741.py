# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki_feed', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wikifeedcommunity',
            options={'verbose_name_plural': 'Wiki feeds', 'verbose_name': 'Wiki feed'},
        ),
    ]

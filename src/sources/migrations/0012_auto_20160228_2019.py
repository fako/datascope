# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0011_wikidataitems'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wikidataitems',
            options={'verbose_name': 'Wikidata items', 'verbose_name_plural': 'Wikidata items'},
        ),
        migrations.AlterModelOptions(
            name='wikipedialistpages',
            options={'verbose_name': 'Wikipedia list pages', 'verbose_name_plural': 'Wikipedia list pages'},
        ),
        migrations.AlterModelOptions(
            name='wikipediarecentchanges',
            options={'verbose_name': 'Wikipedia recent changes', 'verbose_name_plural': 'Wikipedia recent changes'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visual_translations', '0005_visualtranslationsbriccommunity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visualtranslationsbriccommunity',
            options={'verbose_name_plural': 'Visual translations (BRIC)', 'verbose_name': 'Visual translation (BRIC)'},
        ),
        migrations.AlterModelOptions(
            name='visualtranslationseucommunity',
            options={'verbose_name_plural': 'Visual translations (EU)', 'verbose_name': 'Visual translation (EU)'},
        ),
    ]

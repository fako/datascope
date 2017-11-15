# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0019_officialannouncementsdocumentnetherlands_officialannouncementsnetherlands'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wikipediacategories',
            options={'verbose_name_plural': 'Wikipedia categories', 'verbose_name': 'Wikipedia category'},
        ),
        migrations.AlterModelOptions(
            name='wikipediacategorymembers',
            options={'verbose_name_plural': 'Wikipedia category members', 'verbose_name': 'Wikipedia category members'},
        ),
        migrations.AlterModelOptions(
            name='wikipediasearch',
            options={'verbose_name_plural': 'Wikipedia searches', 'verbose_name': 'Wikipedia search'},
        ),
    ]

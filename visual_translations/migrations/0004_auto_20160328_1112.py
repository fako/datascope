# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


sql = """UPDATE django_content_type
         SET model = 'visualtranslationseucommunity'
         WHERE model = 'visualtranslationscommunity' AND
               app_label = 'visual_translations';"""

reverse_sql = """UPDATE django_content_type
                 SET model = 'visualtranslationscommunity'
                 WHERE model = 'visualtranslationseucommunity' AND
                       app_label = 'visual_translations';"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160226_1306'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('visual_translations', '0003_auto_20160225_2307'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql),
        migrations.RenameModel('VisualTranslationsCommunity', 'VisualTranslationsEUCommunity')
    ]

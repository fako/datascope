# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    operations = [
        migrations.CreateModel(
            name='DiscourseSearchCommunity',
            fields=[
            ],
            options={
                'verbose_name': 'Discourse search community',
                'verbose_name_plural': 'Discourse search communities',
                'proxy': True,
            },
            bases=('topic_research.crosscombinetermsearchcommunity',),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0014_wikipediagenerator'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikipediaCategories',
            fields=[
                ('wikipediagenerator_ptr', models.OneToOneField(serialize=False, to='sources.WikipediaGenerator', auto_created=True, primary_key=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('sources.wikipediagenerator',),
        ),
        migrations.CreateModel(
            name='WikipediaCategoryMembers',
            fields=[
                ('wikipediagenerator_ptr', models.OneToOneField(serialize=False, to='sources.WikipediaGenerator', auto_created=True, primary_key=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('sources.wikipediagenerator',),
        ),
    ]

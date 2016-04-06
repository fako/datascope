# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki_news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wikinewscommunity',
            name='state',
            field=models.CharField(default='New', max_length=255, choices=[('Aborted', 'Aborted'), ('New', 'New'), ('Ready', 'Ready'), ('Asynchronous', 'Asynchronous'), ('Synchronous', 'Synchronous')]),
        ),
    ]

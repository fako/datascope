# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0004_communitymock'),
    ]

    operations = [
        migrations.AddField(
            model_name='collective',
            name='community_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collective',
            name='community_type',
            field=models.ForeignKey(related_name='+', default=64, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='growth',
            name='community_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='growth',
            name='community_type',
            field=models.ForeignKey(related_name='+', default=64, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='individual',
            name='community_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='individual',
            name='community_type',
            field=models.ForeignKey(related_name='+', default=64, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
    ]

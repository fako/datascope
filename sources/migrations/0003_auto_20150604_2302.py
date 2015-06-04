# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0002_acteursspotprofile_benfcastingprofile_moederannecastingsearch_moederannecastingsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='acteursspotprofile',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='acteursspotprofile',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='benfcastingprofile',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='benfcastingprofile',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='httpresourcemock',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='httpresourcemock',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='moederannecastingsearch',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='moederannecastingsearch',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='moederannecastingsession',
            name='retainer_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='moederannecastingsession',
            name='retainer_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20160226_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='growth',
            name='contribute',
            field=models.CharField(null=True, blank=True, max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources'), ('ExtractProcessor.extract_from_resource', 'Extract content from one or more resources'), ('ExtractProcessor.pass_resource_through', "Take content 'as is' from one or more resources")]),
        ),
        migrations.AlterField(
            model_name='growth',
            name='contribute_type',
            field=models.CharField(null=True, blank=True, max_length=255, choices=[('Append', 'Append'), ('Inline', 'Inline'), ('Update', 'Update')]),
        ),
        migrations.AlterField(
            model_name='growth',
            name='process',
            field=models.CharField(max_length=255, choices=[('HttpResourceProcessor.fetch', 'Fetch content from HTTP resource'), ('HttpResourceProcessor.fetch_mass', 'Fetch content from multiple HTTP resources'), ('ExtractProcessor.extract_from_resource', 'Extract content from one or more resources'), ('ExtractProcessor.pass_resource_through', "Take content 'as is' from one or more resources")]),
        ),
    ]

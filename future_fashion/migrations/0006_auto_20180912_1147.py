# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-12 11:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('future_fashion', '0005_auto_20180912_1144'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FutureFashionCommunity',
            new_name='ClothingDataCommunity',
        ),
        migrations.AlterModelOptions(
            name='clothingdatacommunity',
            options={'verbose_name': 'Clothing data community', 'verbose_name_plural': 'Clothing data communities'},
        ),
    ]

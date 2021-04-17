# Generated by Django 2.2.13 on 2021-04-17 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nautilus', '0001_squashed_0006_on_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locaforaorderoverviewcommunity',
            name='current_growth',
        ),
        migrations.RemoveField(
            model_name='locaforaorderoverviewcommunity',
            name='kernel_type',
        ),
        migrations.RemoveField(
            model_name='locaforaorders',
            name='retainer_type',
        ),
        migrations.DeleteModel(
            name='LocaforaLogin',
        ),
        migrations.DeleteModel(
            name='LocaforaOrderOverviewCommunity',
        ),
        migrations.DeleteModel(
            name='LocaforaOrders',
        ),
    ]

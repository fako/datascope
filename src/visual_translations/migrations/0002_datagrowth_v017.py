# Generated by Django 3.2 on 2021-05-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visual_translations', '0001_squashed_0010_on_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webimagedownload',
            name='head',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='webimagedownload',
            name='request',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]

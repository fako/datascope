# Generated by Django 3.2.16 on 2022-11-13 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('future_fashion', '0006_remove_indicoio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brandrecognitionservice',
            name='retainer_type',
        ),
        migrations.RemoveField(
            model_name='clothingdatacommunity',
            name='current_growth',
        ),
        migrations.RemoveField(
            model_name='clothingdatacommunity',
            name='kernel_type',
        ),
        migrations.RemoveField(
            model_name='clothingimagedownload',
            name='retainer_type',
        ),
        migrations.RemoveField(
            model_name='clothinginventorycommunity',
            name='current_growth',
        ),
        migrations.RemoveField(
            model_name='clothinginventorycommunity',
            name='kernel_type',
        ),
        migrations.RemoveField(
            model_name='clothingtyperecognitionservice',
            name='retainer_type',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='community_type',
        ),
        migrations.RemoveField(
            model_name='colorclothingset',
            name='bottom_item',
        ),
        migrations.RemoveField(
            model_name='colorclothingset',
            name='top_item',
        ),
        migrations.RemoveField(
            model_name='document',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='document',
            name='community_type',
        ),
        migrations.DeleteModel(
            name='Annotation',
        ),
        migrations.DeleteModel(
            name='BrandRecognitionService',
        ),
        migrations.DeleteModel(
            name='ClothingDataCommunity',
        ),
        migrations.DeleteModel(
            name='ClothingImageDownload',
        ),
        migrations.DeleteModel(
            name='ClothingInventoryCommunity',
        ),
        migrations.DeleteModel(
            name='ClothingTypeRecognitionService',
        ),
        migrations.DeleteModel(
            name='Collection',
        ),
        migrations.DeleteModel(
            name='ColorClothingSet',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
    ]

import os
import shutil

from django.core.management import BaseCommand
from django.core.files.storage import default_storage

from core.utils.helpers import format_datetime

from visual_translations.models import VisualTranslationsEUCommunity


class Command(BaseCommand):

    def handle(self, *args, **options):
        dirs, files = default_storage.listdir('visual_translations')
        for term in dirs:
            euc = VisualTranslationsEUCommunity.objects.get(signature=term)
            time = format_datetime(euc.created_at)
            source_path = default_storage.path('visual_translations/{}'.format(term))
            temp_path = default_storage.path('visual_translations/{}'.format(time))
            destination_path = os.path.join(source_path, time)
            shutil.move(source_path, temp_path)
            os.mkdir(source_path)
            shutil.move(temp_path, destination_path)

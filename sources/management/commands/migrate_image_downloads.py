import os
import logging
from tqdm import tqdm
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.apps import apps

from datagrowth import settings as datagrowth_settings
from core.utils.helpers import ibatch, batchize
from sources.models import ImageDownload


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start', type=str, required=True)
        parser.add_argument('-e', '--end', type=str, required=True)
        parser.add_argument('-m', '--new-model', type=str, required=True)

    def _handle_batch(self, batch, new_model, base_dir):
        Model = apps.get_model(new_model)
        instances = []
        for instance in batch:
            instance.__class__ = Model
            instance.pk = None
            instances.append(instance)
            print("From:", os.path.join(base_dir, instance.body))
            file_path, file_name, extension = instance._get_file_info(instance.request.get("url"))
            file_path = file_path.replace(datagrowth_settings.DATAGROWTH_MEDIA_ROOT + os.sep, "")
            print("To:", os.path.join(file_path, file_name + extension))

    def handle(self, *args, **options):
        media_dir = os.path.join("system", "files", "media")
        start = datetime.strptime(options["start"], "%Y-%m-%d")
        end = datetime.strptime(options["end"], "%Y-%m-%d")
        end += timedelta(days=1)
        batch_size = 10

        queryset = ImageDownload.objects.filter(created_at__gte=start, created_at__lte=end)
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        for batch in batch_iterator:
            self._handle_batch(batch, options["new_model"], media_dir)
            break

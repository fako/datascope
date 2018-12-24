import os
import logging
from tqdm import tqdm
from datetime import datetime, timedelta
import shutil

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

        # Check batch
        Model = apps.get_model(new_model)
        existing_set = Model.objects.filter(uri__in=[instance.uri for instance in batch])
        if existing_set.count() == len(batch):
            log.info("Skipping batch because instances are migrated")
            return

        # Prepare migration
        instances = []
        for instance in batch:
            # Check if source file exist
            source_file = os.path.join(base_dir, instance.body)
            if existing_set.filter(uri=instance.uri).exists():
                log.info("Skipping instance because instance was migrated: {}".format(instance.id))
                continue
            if not os.path.exists(source_file):
                log.warning("Skipping instance because file is missing: {}".format(instance.id))
                continue
            # Basic model transfer
            instance.__class__ = Model
            instance.pk = None
            # Check destination and copy
            file_path, file_name, extension = instance._get_file_info(instance.request.get("url"))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            dest_file = os.path.join(file_path, file_name + extension)
            shutil.copy2(source_file, dest_file)
            # Update instance info
            instance.body = dest_file.replace(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, "").lstrip()
            instances.append(instance)

        # Execute migration
        Model.objects.batch_create(instances)

    def handle(self, *args, **options):
        media_dir = os.path.join("system", "files", "media")
        start = datetime.strptime(options["start"], "%Y-%m-%d")
        end = datetime.strptime(options["end"], "%Y-%m-%d")
        end += timedelta(days=1)
        batch_size = 100

        queryset = ImageDownload.objects.filter(created_at__gte=start, created_at__lte=end)
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        for batch in batch_iterator:
            self._handle_batch(batch, options["new_model"], media_dir)
            break

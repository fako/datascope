import json
import os
import logging
from tqdm import tqdm
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.apps import apps
from django.core import serializers

from core.utils.helpers import ibatch, batchize
from sources.models import ImageDownload


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start', type=str, required=True)
        parser.add_argument('-e', '--end', type=str, required=True)
        parser.add_argument('-m', '--new-model', type=str, required=True)

    def _handle_batch(self, batch, new_model, base_dir):
        raw_json = serializers.serialize("json", batch)
        model = apps.get_model(new_model)
        data = []
        for record in json.loads(raw_json):
            record["fields"]["model"] = new_model
            del record["pk"]
            data.append(record)
        print(data[:10])

    def handle(self, *args, **options):
        media_dir = os.path.join("system", "files", "media")
        start = datetime.strptime(options["start"], "%Y-%m-%d")
        end = datetime.strptime(options["end"], "%Y-%m-%d")
        end += timedelta(days=1)
        batch_size = 500

        queryset = ImageDownload.objects.filter(created_at__gte=start, created_at__lte=end)
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        for batch in batch_iterator:
            self._handle_batch(batch, options["new_model"], media_dir)
            break

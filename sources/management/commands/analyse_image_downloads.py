import pandas as pd
import logging
from tqdm import tqdm

from django.core.management.base import BaseCommand

from core.utils.helpers import ibatch, batchize
from sources.models import ImageDownload


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def handle(self, *args, **options):
        batch_size = 500
        columns = ["created_at", "body", "uri", "status"]
        queryset = ImageDownload.objects.values(*columns)
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        df = None
        for records in batch_iterator:
            batch_frame = pd.DataFrame.from_records(records, index=["created_at"])
            if df is None:
                df = batch_frame
            else:
                df = pd.concat([df, batch_frame])  # TODO: add sort=False when upgrading pandas to 0.23

        print(df.groupby("status").size())
        print()
        print()
        groups = df.groupby(pd.Grouper(freq='D')).size()
        groups = groups[groups > 0]
        print(groups)


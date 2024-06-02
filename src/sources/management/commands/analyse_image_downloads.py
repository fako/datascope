import os
import pandas as pd
import logging

from django.core.management.base import BaseCommand
from django.apps import apps

from datagrowth.utils import ibatch


log = logging.getLogger("datascope")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', type=str, default="sources.ImageDownload")
        parser.add_argument('-d', '--dir', type=str, default=os.path.join("system", "files", "media"))

    def handle(self, *args, **options):
        Model = apps.get_model(options["model"])
        media_dir = options["dir"]
        batch_size = 500
        columns = ["created_at", "body", "uri"]
        queryset = Model.objects.values(*columns)
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size, progress_bar=True, total=count)
        df = None
        for records in batch_iterator:
            batch_frame = pd.DataFrame.from_records(records, index=["created_at"])
            batch_frame["does_exist"] = batch_frame.apply(
                lambda row: os.path.exists(os.path.join(media_dir, row["body"])),
                axis=1
            )
            if df is None:
                df = batch_frame
            else:
                df = pd.concat([df, batch_frame], sort=False)

        valid = df[df["does_exist"]]
        invalid = df[~df["does_exist"]]

        groups = valid.groupby(pd.Grouper(freq='D')).size()
        groups = groups[groups > 0]
        print(groups)
        print()
        print()
        print("-" * 80)
        print()
        print()
        groups = invalid.groupby(pd.Grouper(freq='D')).size()
        groups = groups[groups > 0]
        print(groups)

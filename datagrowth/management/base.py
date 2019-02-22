from datetime import datetime
import logging

from django.apps import apps
from django.core.management.base import BaseCommand

from datagrowth.configuration import DecodeConfigAction
from datagrowth.datatypes import DatasetState


log = logging.getLogger("datagrowth.command")


class DatasetCommand(BaseCommand):
    """
    Base command for Dataset centered commands
    """
    dataset_model = ""

    def add_arguments(self, parser):
        parser.add_argument('dataset', type=str, nargs="?", default=self.dataset_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def handle_dataset(self, dataset, *arguments, **options):
        raise NotImplementedError("You should implement the handle_dataset method.")

    def get_dataset(self):
        dataset, created = self.model.objects.get_latest_or_create_by_signature(self.signature, **self.config)
        return dataset

    def get_datasets(self):
        return self.model.objects.filter(state=DatasetState.READY).iterator()

    def handle(self, *args, **options):
        Dataset = apps.get_model(options.pop("dataset"))
        self.model = Dataset
        self.config = options["config"]
        self.signature = getattr(self, "signature", Dataset.get_signature_from_input(*args, **self.config))
        self.signature = self.signature or None

        if self.signature is not None:
            datasets = [self.get_dataset()]
        else:
            datasets = self.get_datasets()

        log.info("Target: {}".format(self.signature or Dataset.__class__.__name__))

        for dataset in datasets:
            log.info("Dataset: {}".format(dataset))
            log.info("Start: {}".format(datetime.now()))
            self.handle_dataset(dataset, *args, **options)
            log.info("End: {}".format(datetime.now()))

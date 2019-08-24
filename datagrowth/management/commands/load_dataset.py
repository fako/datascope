import logging
import os
from tqdm import tqdm
import json
import re

from django.apps import apps
from django.core.serializers import deserialize
from django.contrib.contenttypes.models import ContentType

from datagrowth.management.base import DatasetCommand
from datagrowth.utils import get_dumps_path


log = logging.getLogger("datagrowth.command")


class Command(DatasetCommand):
    """
    Loads a dataset by signature
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-t', '--transform-community', action="store_true")

    def get_dataset(self):  # patches the model to act like a proper dataset
        self.model.signature = self.signature
        return self.model

    def get_datasets(self):
        datasets = []
        for entry in os.scandir(get_dumps_path(self.model)):
            if entry.is_file() and not entry.name.startswith("."):
                instance = self.model()
                file_match = re.search("(?P<signature>.+?)\.?(?P<pk>\d+)?\.json$", entry.name)
                file_info = file_match.groupdict()
                instance.signature = file_info["signature"]
                instance.file_path = entry.path  # this property gets added especially for the command
                datasets.append(instance)
        return datasets

    def bulk_create_objects(self, objects, transform_community):

        obj = objects[0]
        model = type(obj)

        if transform_community:
            if isinstance(obj, self.Individual):
                model = self.Document
                for obj in objects:
                    collection_id = obj.collective_id if obj.collective_id else None
                    obj.__class__ = model
                    obj.collection_id = collection_id
                    if isinstance(obj.properties, str):
                        obj.properties = json.loads(obj.properties)
            elif isinstance(obj, self.Collective):
                model = self.Collection
                for obj in objects:
                    obj.__class__ = model
            elif isinstance(obj, self.Growth):
                for obj in objects:
                    obj.input_type = ContentType.objects.get_for_model(
                        self.Document if isinstance(obj.input, self.Individual) else self.Collection
                    )
                    obj.output_type = ContentType.objects.get_for_model(
                        self.Document if isinstance(obj.output, self.Individual) else self.Collection
                    )
            else:
                obj.kernel_type = ContentType.objects.get_for_model(
                    self.Document if isinstance(obj.kernel, self.Individual) else self.Collection
                )

        model.objects.bulk_create(objects)

    def handle_dataset(self, dataset, *args, **options):
        transform_community = options.get("transform_community", False)
        if transform_community:
            log.info("Using transformation to change all data storage into Document and Collection")
            self.Growth = apps.get_model("core", "Growth")
            self.Document = apps.get_model(dataset._meta.app_label, "Document")
            self.Individual = apps.get_model("core", "Individual")
            self.Collection = apps.get_model(dataset._meta.app_label, "Collection")
            self.Collective = apps.get_model("core", "Collective")
        if not os.path.exists(dataset.file_path):
            log.error("Dump with signature {} does not exist".format(dataset.signature))
            exit(1)
        with open(dataset.file_path, "r") as dump_file:
            batch_count = 0
            for _ in dump_file.readlines():
                batch_count += 1
            dump_file.seek(0)
            for line in tqdm(dump_file, total=batch_count):
                objects = [wrapper.object for wrapper in deserialize("json", line)]
                self.bulk_create_objects(objects, transform_community)

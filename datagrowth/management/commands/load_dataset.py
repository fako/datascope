import logging
import os
from tqdm import tqdm

from django.apps import apps
from django.core.serializers import deserialize

from datagrowth.management.base import DatasetCommand
from datagrowth.utils import get_dumps_path


log = logging.getLogger("datagrowth.command")


class Command(DatasetCommand):
    """
    Loads a dataset by signature
    """

    # def add_arguments(self, parser):
    #     super().add_arguments(parser)
    #     parser.add_argument('-t', '--transform-community', action="store_true")

    def get_dataset(self):  # patches the model to act like a proper dataset
        self.model.signature = self.signature
        return self.model

    def get_datasets(self):
        datasets = []
        for entry in os.scandir(get_dumps_path(self.model)):
            if entry.is_file() and not entry.name.startswith("."):
                instance = self.model()
                instance.signature = entry.name[:-5]
                datasets.append(instance)
        return datasets

    def bulk_create_objects(self, objects, transform_community):
        obj = objects[0]
        model = type(obj)
        # if transform_community and isinstance(model, (self.Individual, self.Collective,)):
        #     target_class = self.Document.__class__ if isinstance(obj, self.Individual) else self.Collection.__class__
        #     log.info("Transforming {} into {}".format(obj.__class__.__name__, target_class.__name__))
        #     for obj in objects:
        #         obj.__class__ = target_class
        model.objects.bulk_create(objects)

    def handle_dataset(self, dataset, *args, **options):
        # transform_community = options.get("transform_community", False)
        # if transform_community:
        #     self.Document = apps.get_model(dataset._meta.app_label, "Document")
        #     self.Individual = apps.get_model("core", "Individual")
        #     self.Collection = apps.get_model(dataset._meta.app_label, "Collection")
        #     self.Collective = apps.get_model("core", "Collective")
        source = get_dumps_path(dataset)
        file_name = os.path.join(source, "{}.json".format(dataset.signature))
        if not os.path.exists(file_name):
            log.error("Dump with signature {} does not exist".format(dataset.signature))
            exit(1)
        with open(file_name, "r") as dump_file:
            batch_count = 0
            for _ in dump_file.readlines():
                batch_count += 1
            dump_file.seek(0)
            for line in tqdm(dump_file, total=batch_count):
                objects = [wrapper.object for wrapper in deserialize("json", line)]
                self.bulk_create_objects(objects, False)

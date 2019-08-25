import os

from datagrowth.management.base import DatasetCommand
from datagrowth.utils import get_dumps_path, object_to_disk, queryset_to_disk


class Command(DatasetCommand):
    """
    Dumps a dataset by signature
    """

    def handle_dataset(self, dataset, *args, **options):
        setattr(dataset, "current_growth", None)  # resets the dataset
        destination = get_dumps_path(dataset)
        if not os.path.exists(destination):
            os.makedirs(destination)
        file_name = os.path.join(destination, "{}.{}.json".format(dataset.signature, dataset.id))
        with open(file_name, "w") as json_file:
            object_to_disk(dataset, json_file)
            queryset_to_disk(dataset.growth_set, json_file)
            queryset_to_disk(dataset.collections, json_file)
            queryset_to_disk(dataset.documents, json_file)

import os

from django.core.serializers import serialize

from datagrowth.management.base import DatasetCommand
from datagrowth.utils import ibatch, get_dumps_path


class Command(DatasetCommand):
    """
    Dumps a dataset by signature
    """

    @staticmethod
    def queryset_to_disk(queryset, json_file, batch_size=100):
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size, progress_bar=True, total=count)
        for batch in batch_iterator:
            batch_data = serialize("json", batch, use_natural_foreign_keys=True)
            json_file.writelines([batch_data + "\n"])

    @staticmethod
    def object_to_disk(object, json_file):
        setattr(object, "current_growth", None)  # resets dataset
        batch_data = serialize("json", [object], use_natural_foreign_keys=True)
        json_file.write(batch_data + "\n")

    def handle_dataset(self, dataset, *args, **options):
        destination = get_dumps_path(dataset)
        if not os.path.exists(destination):
            os.makedirs(destination)
        file_name = os.path.join(destination, "{}.json".format(dataset.signature))
        with open(file_name, "w") as json_file:
            self.object_to_disk(dataset, json_file)
            self.queryset_to_disk(dataset.growth_set, json_file)
            self.queryset_to_disk(dataset.collective_set, json_file)
            self.queryset_to_disk(dataset.individual_set, json_file)

import os

from django.core.management.base import LabelCommand
from django.apps import apps

from datagrowth.utils import get_dumps_path, queryset_to_disk


class Command(LabelCommand):
    """
    Dumps all objects from a Resource to file
    """

    def handle_label(self, label, **options):
        Resource = apps.get_model(label)
        destination = get_dumps_path(Resource)
        if not os.path.exists(destination):
            os.makedirs(destination)
        resource_name = Resource.get_name()
        file_path = os.path.join(destination, "{}.dump.json".format(resource_name))
        with open(file_path, "w") as dump_file:
            queryset_to_disk(Resource.objects, dump_file)

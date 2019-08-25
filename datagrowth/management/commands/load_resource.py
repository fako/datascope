import logging
import os

from django.core.management.base import LabelCommand
from django.apps import apps

from datagrowth.utils import get_dumps_path, objects_from_disk


log = logging.getLogger("datagrowth.command")


class Command(LabelCommand):
    """
    Loads all objects from a Resource dump file
    """

    def handle_label(self, label, **options):
        Resource = apps.get_model(label)
        source = get_dumps_path(Resource)
        resource_name = Resource.get_name()
        file_path = os.path.join(source, "{}.dump.json".format(resource_name))
        if not os.path.exists(file_path):
            log.error("Resource dump {} does not exist".format(file_path))
            exit(1)
        with open(file_path, "r") as dump_file:
            for objects in objects_from_disk(dump_file):
                Resource.objects.bulk_create(objects)

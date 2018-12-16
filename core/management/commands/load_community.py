import os
from tqdm import tqdm

from django.core.serializers import deserialize

from core.management.commands import CommunityCommand


class Command(CommunityCommand):
    """
    Loads a community by signature
    """

    def get_community(self):
        return self.model

    def bulk_create_objects(self, objects):
        obj = objects[0]
        model = type(obj)
        model.objects.bulk_create(objects)

    def handle_community(self, community, *args, **options):
        source = os.path.join("data", community._meta.app_label, "dumps", community.get_name())
        file_name = os.path.join(source, "{}.json".format(self.signature))
        if not os.path.exists(file_name):
            print("Dump with signature {} does not exist".format(self.signature))
            exit(1)
        with open(file_name, "r") as dump_file:
            batch_count = 0
            for _ in dump_file.readlines():
                batch_count += 1
            dump_file.seek(0)
            for line in tqdm(dump_file, total=batch_count):
                objects = [wrapper.object for wrapper in deserialize("json", line)]
                self.bulk_create_objects(objects)

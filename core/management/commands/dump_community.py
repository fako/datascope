import os
from tqdm import tqdm

from django.core.serializers import serialize

from core.management.commands import CommunityCommand
from core.utils.helpers import ibatch, batchize


class Command(CommunityCommand):
    """
    Dumps a community by signature
    """

    @staticmethod
    def queryset_to_disk(queryset, json_file, batch_size=100):
        count = queryset.all().count()
        batch_iterator = ibatch(queryset.iterator(), batch_size=batch_size)
        if count >= batch_size * 5:
            batches, rest = batchize(count, batch_size)
            batch_iterator = tqdm(batch_iterator, total=batches)
        for batch in batch_iterator:
            batch_data = serialize("json", batch, use_natural_foreign_keys=True)
            json_file.writelines([batch_data + "\n"])

    @staticmethod
    def object_to_disk(object, json_file):
        setattr(object, "current_growth", None)  # resets community
        batch_data = serialize("json", [object], use_natural_foreign_keys=True)
        json_file.write(batch_data + "\n")

    def handle_community(self, community, *args, **options):
        destination = os.path.join(community._meta.app_label, "data", "dumps", community.get_name())
        if not os.path.exists(destination):
            os.makedirs(destination)
        file_name = os.path.join(destination, "{}.json".format(community.signature))
        with open(file_name, "w") as json_file:
            self.object_to_disk(community, json_file)
            self.queryset_to_disk(community.growth_set, json_file)
            self.queryset_to_disk(community.collective_set, json_file)
            self.queryset_to_disk(community.individual_set, json_file)

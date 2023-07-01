import json

from datagrowth.management.base import DatasetCommand
from core.utils.configuration import DecodeConfigAction


class Command(DatasetCommand):

    dataset_model = "visual_translations.VisualTranslationsEUCommunity"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-l', '--country', type=str, nargs="?", default="")
        parser.add_argument('-w', '--word', type=str, nargs="?", default="")

    def handle_dataset(self, dataset, *arguments, **options):
        word_encoded = json.dumps(options["word"])
        qs = dataset.documents.filter(properties__contains="word\": {}".format(word_encoded))
        if options["country"]:
            country = json.dumps(options["country"])
            qs = qs.filter(properties__contains="country\": {}".format(country))
        print("Deleting {} documents".format(qs.count()))
        qs.delete(); print("Deleted")

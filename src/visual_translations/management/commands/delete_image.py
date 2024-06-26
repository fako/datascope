from datagrowth.management.base import DatasetCommand


class Command(DatasetCommand):

    cast_as_community = True
    dataset_model = "visual_translations.VisualTranslationsEUCommunity"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-s', '--src', type=str, nargs="?", default="")

    def handle_community(self, dataset, **options):
        qs = dataset.documents.filter(properties__contains=options["src"])
        print("Deleting {} documents".format(qs.count()))
        for ind in qs:
            print(ind.properties)

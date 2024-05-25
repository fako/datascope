from datagrowth.management.base import DatasetCommand


class Command(DatasetCommand):

    cast_as_community = True
    dataset_model = "visual_translations.VisualTranslationsEUCommunity"

    def handle_community(self, dataset, *arguments, **options):
        dataset.finish_download(None, None)

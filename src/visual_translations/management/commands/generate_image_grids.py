from datagrowth.management.base import DatasetCommand


class Command(DatasetCommand):

    dataset_model = "visual_translations.VisualTranslationsEUCommunity"

    def handle_dataset(self, dataset, *arguments, **options):
        dataset.finish_download(None, None)

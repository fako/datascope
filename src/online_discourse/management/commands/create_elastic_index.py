import logging

from django.conf import settings

from datagrowth.management.base import DatasetCommand

from online_discourse.discourse import configurations
from online_discourse.models import ElasticIndex
from online_discourse.elastic import get_index_config


log = logging.getLogger("datagrowth")


class Command(DatasetCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-r', '--recreate', action="store_true")
        parser.add_argument('-p', '--promote', action="store_true")

    def handle_dataset(self, dataset, *args, **options):

        configuration_name = next(arg for arg in dataset.signature.split("&") if "=" not in arg)
        configuration = getattr(configurations, configuration_name)
        if configuration.language not in settings.ELASTIC_SEARCH_ANALYSERS:
            log.error(f"Can't create index for {configuration.title} because {configuration.language} is not supported")
            return

        recreate = options["recreate"]
        promote = options["promote"]
        print(f"Creating index for { configuration.title }; "
              f"language:{configuration.language}, recreate:{recreate} and documents:{dataset.documents.count()}")

        elastic_configuration = get_index_config(configuration.language)
        index, created = ElasticIndex.objects.get_or_create(
            signature=dataset.signature,
            language=configuration.language,
            defaults={
                "dataset": dataset,
                "configuration": elastic_configuration
            }
        )
        index.clean()
        index.push((doc.to_search() for doc in dataset.kernel.document_set.all()), recreate=recreate)
        index.save()
        if promote:
            print(f"Promoting index { index.remote_name } to latest")
            index.promote_to_latest()

        log.info(f'{configuration.title} errors:{index.error_count}')

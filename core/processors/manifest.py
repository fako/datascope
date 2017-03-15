import logging

from celery import current_app as app

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.individual import Individual
from core.models.resources.manifestation import Manifestation
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty, load_config
from core.utils.helpers import get_any_model
from core.views.community import CommunityView


log = logging.getLogger("datascope")


class ManifestProcessor(Processor):

    ARGS_BATCH_METHODS = ['manifest_mass']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="manifest_processor"
    )

    def __init__(self, config):
        super(ManifestProcessor, self).__init__(config)
        assert "_community" in config or "community" in config, \
            "ManifestProcessor expects a community that it should manifest in the configuration."
        self._community = None

    def manifest_from_individuals(self, individuals):
        for individual in individuals:
            args = Individual.output_from_content(individual, self.config.args)
            kwargs = Individual.output_from_content(individual, self.config.kwargs)
            ManifestProcessor._manifest(config=self.config, *args, **kwargs)
            yield individual

    def results(self, result):
        scc_ids, err_ids = result
        scc = Manifestation.objects.filter(id__in=scc_ids)
        err = Manifestation.objects.filter(id__in=err_ids)
        return scc, err

    @staticmethod
    @app.task(name="Manifest.manifest")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _manifest(config, *args, **kwargs):
        success = []
        errors = []
        community_model = get_any_model(config.community)
        signature = community_model.get_signature_from_input(*args, **kwargs)
        config = community_model.get_configuration_from_input(*args, **kwargs)
        community_instance = community_model.objects.get_latest_by_signature(signature, **kwargs)
        community_path = CommunityView.get_full_path(community_model, "/".join(args), kwargs)
        manifestation = Manifestation(uri=community_path, community=community_instance, config=config)
        manifestation.save()
        manifestation.get_data()
        success.append(manifestation.id)
        return [success, errors]

    @staticmethod
    @app.task(name="Manifest.manifest_serie")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _manifest_serie(config, args_list, kwargs_list):
        success = []
        errors = []
        for args, kwargs in zip(args_list, kwargs_list):
            scc, err = ManifestProcessor._manifest(config=config, *args, **kwargs)
            success += scc
            errors += err
        return [success, errors]

    @property
    def manifest_mass(self):
        return self._manifest_serie.s(
            config=self.config.to_dict(private=True, protected=True)
        )

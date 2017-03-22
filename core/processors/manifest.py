import logging

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.individual import Individual
from core.models.resources.manifestation import Manifestation
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty
from core.tasks import manifest, manifest_serie


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
            manifest(config=self.config, *args, **kwargs)
            yield individual

    def results(self, result):
        scc_ids, err_ids = result
        scc = Manifestation.objects.filter(id__in=scc_ids)
        err = Manifestation.objects.filter(id__in=err_ids)
        return scc, err

    @property
    def manifest_mass(self):
        return manifest_serie.s(
            config=self.config.to_dict(private=True, protected=True)
        )

import logging

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.individual import Individual
from core.tasks import manifest, manifest_serie
from core.processors.resources.base import ResourceProcessor
from core.utils.configuration import ConfigurationProperty


log = logging.getLogger("datascope")


class ManifestProcessor(ResourceProcessor):

    ARGS_BATCH_METHODS = ['manifest_mass']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="manifest_processor"
    )

    def __init__(self, config):
        config.update({
            "_resource": "Manifestation"
        })
        super(ManifestProcessor, self).__init__(config)
        assert "_community" in config or "community" in config, \
            "ManifestProcessor expects a community that it should manifest in the configuration."

    def manifest_from_individuals(self, individuals):
        for individual in individuals:
            args = Individual.output_from_content(individual, self.config.args)
            kwargs = Individual.output_from_content(individual, self.config.kwargs)
            manifest(config=self.config, *args, **kwargs)
            yield individual

    @property
    def manifest_mass(self):
        return manifest_serie.s(
            config=self.config.to_dict(private=True, protected=True)
        )

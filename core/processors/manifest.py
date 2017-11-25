import logging

from celery.result import AsyncResult, states as TaskStates

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.individual import Individual
from core.models.resources.manifestation import Manifestation
from core.tasks import manifest, manifest_serie
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty
from core.exceptions import DSProcessUnfinished, DSProcessError


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

    def manifest_from_individuals(self, individuals):
        for individual in individuals:
            args = Individual.output_from_content(individual, self.config.args)
            kwargs = Individual.output_from_content(individual, self.config.kwargs)
            manifest(config=self.config, *args, **kwargs)
            yield individual

    @staticmethod
    def async_results(result_id):
        async_result = AsyncResult(result_id)
        if not async_result.ready():
            raise DSProcessUnfinished("Result with id {} is not ready.".format(result_id))
        if async_result.status != TaskStates.SUCCESS:
            raise DSProcessError("An error occurred during background processing.")
        return async_result.result

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

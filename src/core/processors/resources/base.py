from django.apps import apps
from celery.result import AsyncResult, states as TaskStates

from datagrowth.processors.base import Processor
from core.exceptions import DSProcessUnfinished, DSProcessError


class ResourceProcessor(Processor):
    # TODO: make sphinx friendly and doc all methods
    """
    A collection of Celery tasks that share their need for specific a configuration.
    Each task should return a single list of ids to be further handled classes like Growth.

    The configuration must include
    - a HttpResource class name to be loaded with Django
    - a guideline to how deep a single resource should collect data
    """

    def __init__(self, config):
        super(ResourceProcessor, self).__init__(config)
        assert "_resource" in config or "resource" in config, \
            "HttpResourceProcessor expects a resource that it should fetch in the configuration."
        self._resource = None

    #######################################################
    # Interface
    #######################################################

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
        scc = self.resource.objects.filter(id__in=scc_ids)
        err = self.resource.objects.filter(id__in=err_ids)
        return scc, err

    #######################################################
    # Getters
    #######################################################

    @property
    def resource(self):
        if not self._resource:
            self._resource = apps.get_model(self.config.resource)
        return self._resource

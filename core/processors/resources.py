import requests

from celery.result import AsyncResult, states as TaskStates

from datascope.configuration import DEFAULT_CONFIGURATION
from core.tasks.http import send, send_mass
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty
from core.utils.helpers import get_any_model
from core.exceptions import DSProcessUnfinished, DSProcessError


class HttpResourceProcessor(Processor):
    # TODO: make sphinx friendly and doc all methods
    """
    A collection of Celery tasks that share their need for specific a configuration.
    Each task should return a single list of ids to be further handled classes like Growth.

    The configuration must include
    - a HttpResource class name to be loaded with Django
    - a guideline to how deep a single resource should collect data
    """

    ARGS_BATCH_METHODS = ['fetch_mass', 'submit_mass']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=["_resource", "_continuation_limit", "_batch_size"],
        namespace="http_resource"
    )

    def __init__(self, config):
        super(HttpResourceProcessor, self).__init__(config)
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
            self._resource = get_any_model(self.config.resource)
        return self._resource

    @classmethod
    def get_session(cls, config):
        return requests.Session()

    #######################################################
    # TASKS
    #######################################################
    # Wrappers that act as an interface
    # to background retrieval of resources

    @property
    def fetch(self):
        return send.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True),
            session=self.__class__.__name__
        )

    @property
    def fetch_mass(self):
        return send_mass.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True),
            session=self.__class__.__name__
        )

    @property
    def submit(self):
        return send.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True),
            session=self.__class__.__name__
        )

    @property
    def submit_mass(self):
        return send_mass.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True),
            session=self.__class__.__name__
        )

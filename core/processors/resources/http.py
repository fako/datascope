import requests

from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.resources.base import ResourceProcessor
from core.tasks.http import send, send_mass
from core.utils.configuration import ConfigurationProperty


class HttpResourceProcessor(ResourceProcessor):

    ARGS_BATCH_METHODS = ['fetch_mass', 'submit_mass']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=["_resource", "_continuation_limit", "_batch_size"],
        namespace="http_resource"
    )

    #######################################################
    # Getters
    #######################################################

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

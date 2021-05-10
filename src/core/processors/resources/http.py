from datagrowth.configuration import ConfigurationProperty
from datagrowth.resources.http.tasks import send, send_mass
from core.processors.resources.base import ResourceProcessor


class HttpResourceProcessor(ResourceProcessor):

    ARGS_BATCH_METHODS = ['fetch_mass', 'submit_mass']

    config = ConfigurationProperty(
        namespace="http_resource",
        private=["_resource", "_continuation_limit"]
    )

    #######################################################
    # TASKS
    #######################################################
    # Wrappers that act as an interface
    # to background retrieval of resources

    @property
    def fetch(self):
        return send.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def fetch_mass(self):
        return send_mass.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def submit(self):
        return send.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def submit_mass(self):
        return send_mass.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True)
        )

from django.apps import apps as django_apps

from celery.contrib.methods import task

from core.utils.configuration import ConfigurationProperty
from core.configuration import DEFAULT_CONFIGURATION


class HttpResourceProcessor(object):
    """
    A collection of Celery tasks that share their need for specific a configuration.
    Each task should return a single list of ids to be further handled by Growth instances.

    The configuration must include
    - a HttpResource class name to be loaded with Django
    - a guideline to how deep a single resource should collect data
    """
    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=['_resource'],
        namespace=""
    )

    def __init__(self, configuration):
        super(HttpResourceProcessor, self).__init__()
        assert isinstance(configuration, dict) and "_resource" in configuration, \
            "HttpFetch expects a resource that it should fetch in the configuration."
        if "continuation_limit" not in configuration:
            configuration["continuation_limit"] = 1
        self.config = configuration

    def get_link(self):
        Resource = django_apps.get_model("core", self.config.resource)
        return Resource(config=self.config.to_dict(protected=True))

    @task(name="HttpFetch.fetch")
    def fetch(self, *args, **kwargs):
        link = self.get_link()
        link.get(*args, **kwargs)
        link.save()
        return [link.id]

    def fetch_mass(self, *args, **kwargs):
        pass

    def submit(self, *args, **kwargs):
        pass

    def submit_mass(self, *args, **kwargs):
        pass

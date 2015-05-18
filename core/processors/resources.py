from django.apps import apps as django_apps

from celery import current_app as app
from celery.contrib.methods import task_method

from core.utils.configuration import ConfigurationProperty, load_config
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
        private=["_resource", "_configuration_limit", "_batch_size"],
        namespace=""
    )

    def __init__(self, configuration):
        super(HttpResourceProcessor, self).__init__()
        assert isinstance(configuration, dict) and "_resource" in configuration, \
            "HttpFetch expects a resource that it should fetch in the configuration."

        if "continuation_limit" not in configuration:
            configuration["_continuation_limit"] = 1
        if "batch_size" not in configuration:
            configuration["_batch_size"] = 0

        self.config = configuration

    def get_link(self):
        Resource = django_apps.get_model("core", self.config.resource)
        return Resource(config=self.config.to_dict(protected=True))

    @app.task(name="HttpFetch.fetch", filter=task_method)
    def fetch(self, *args, **kwargs):
        print self
        print args
        print kwargs
        # Set vars
        results = []
        has_next_request = True
        current_request = {}
        count = 0
        limit = self.config.continuation_limit
        # Continue as long as there are subsequent requests
        while has_next_request and count < limit:
            # Get payload
            link = self.get_link()
            link.request = current_request
            link.get(*args, **kwargs)
            link.save()
            results.append(link.id)
            # Prepare next request
            has_next_request = current_request = link.create_next_request()
            count += 1
        # Output results
        return results

    def fetch_mass(self, *args, **kwargs):
        pass

    def submit(self, *args, **kwargs):
        pass

    def submit_mass(self, *args, **kwargs):
        pass

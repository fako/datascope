from django.db.models.loading import get_model

from celery.contrib.methods import task

from core.utils.configuration import ConfigurationProperty


class HttpResourceProcessor(object):
    """
    Retrieves a single http resource from the web and stores it as HyperText. Possibly returns a cached result.
    """
    def __init__(self, configuration):
        assert isinstance(configuration, dict) and "_resource" in configuration, \
            "HttpFetch expects a resource that it should fetch in the configuration."
        self.config = ConfigurationProperty(
            "_config",
            defaults=configuration,
            private=['_resource']
        )

    @task(name="HttpFetch.fetch")
    def fetch(self, *args, **kwargs):
        Resource = get_model(self.config.resource)
        link = Resource(config=self.config.to_dict(protected=True))
        link.get(*args, **kwargs)

    def fetch_mass(self, *args, **kwargs):
        pass


class HttpFetchMass(object):
    """
    Retrieves multiple http resources at the same time.
    """
    pass
# noinspection PyUnresolvedReferences
from six.moves import zip
from time import sleep

import requests

from django.apps import apps as django_apps

from celery import current_app as app

from datascope.configuration import DEFAULT_CONFIGURATION
from core.utils.configuration import ConfigurationProperty, load_config
from core.exceptions import DSHttpResourceError


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
        private=["_resource", "_continuation_limit", "_batch_size"],
        namespace="http_resource"
    )

    def __init__(self, config):
        super(HttpResourceProcessor, self).__init__()
        assert isinstance(config, dict) and ("_resource" in config or "resource" in config), \
            "HttpFetch expects a resource that it should fetch in the configuration."
        self.config = config

    @staticmethod
    def get_link(config, session=None):
        Resource = django_apps.get_model("sources", config.resource)
        link = Resource(config=config.to_dict(protected=True))
        if session is not None:
            link.session = session
        # FEATURE: update session to use proxy when configured
        # FEATURE: update session to use custom user agents when configured
        return link

    @property
    def fetch(self):
        return self._fetch.s(
            config=self.config.to_dict(private=True, protected=True)
        )

    @staticmethod
    @app.task(name="HttpFetch.fetch")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _fetch(config, *args, **kwargs):
        # Set vars
        session = kwargs.pop("session", None)
        success = []
        errors = []
        has_next_request = True
        current_request = {}
        count = 0
        limit = config.continuation_limit or 1
        # Continue as long as there are subsequent requests
        while has_next_request and count < limit:
            # Get payload
            link = HttpResourceProcessor.get_link(config, session)
            link.request = current_request
            try:
                link = link.get(*args, **kwargs)
                link.save()
                success.append(link.id)
            except DSHttpResourceError:
                link.save()
                errors.append(link.id)
            # Prepare next request
            has_next_request = current_request = link.create_next_request()
            count += 1
        # Output results in simple type for json serialization
        return [success, errors]

    @property
    def fetch_mass(self):
        return self._fetch_mass.s(
            config=self.config.to_dict(private=True, protected=True)
        )

    @staticmethod
    @app.task(name="HttpFetch.fetch_mass")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _fetch_mass(config, args_list, kwargs_list, session=None):
        # FEATURE: chain "batches" of fetch_mass if configured through batch_size
        # FEATURE: concat requests using concat_args_with configuration
        success = []
        errors = []
        if session is None:
            session = requests.Session()
        for args, kwargs in zip(args_list, kwargs_list):
            # Get the results
            scc, err = HttpResourceProcessor._fetch(config=config, session=session, *args, **kwargs)
            success += scc
            errors += err
            # Take a break for scraping if configured
            interval_duration = config.interval_duration / 1000.000
            if interval_duration:
                sleep(interval_duration)
        return [success, errors]

    def submit(self, *args, **kwargs):
        pass

    def submit_mass(self, *args, **kwargs):
        pass

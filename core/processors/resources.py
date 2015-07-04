from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import zip, range

from time import sleep
import logging

import requests

from celery import current_app as app
from celery.result import AsyncResult, states as TaskStates

from datascope.configuration import DEFAULT_CONFIGURATION
from core.utils.configuration import ConfigurationProperty, ConfigurationType, load_config
from core.utils.helpers import get_any_model
from core.exceptions import DSResourceException, DSProcessUnfinished, DSProcessError

log = logging.getLogger("datascope")


class HttpResourceProcessor(object):
    # TODO: make sphinx friendly and doc all methods
    """
    A collection of Celery tasks that share their need for specific a configuration.
    Each task should return a single list of ids to be further handled classes like Growth.

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
            "HttpResourceProcessor expects a resource that it should fetch in the configuration."
        self.config = config
        self._resource = None

    #######################################################
    # Interface
    #######################################################

    @staticmethod
    def async_results(result_id):  # TODO: test
        async_result = AsyncResult(result_id)
        if not async_result.ready():
            raise DSProcessUnfinished("Result with id {} is not ready.".format(result_id))
        if async_result.status != TaskStates.SUCCESS:
            raise DSProcessError("An error occurred during background processing.")  # TODO: reraise with celery trace?
        return async_result.result

    def results(self, result):  # TODO: test
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

    @staticmethod
    def get_link(config, session=None):
        assert isinstance(config, ConfigurationType), "get_link expects a fully prepared ConfigurationType for config"
        Resource = get_any_model(config.resource)
        link = Resource(config=config.to_dict(protected=True))
        if session is not None:
            link.session = session
        # FEATURE: update session to use proxy when configured
        # FEATURE: update session to use custom user agents when configured
        return link

    #######################################################
    # PRIVATE
    #######################################################
    # Celery tasks to fetch resources in background.

    @staticmethod
    @app.task(name="HttpFetch.send")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _send(config, *args, **kwargs):
        # Set vars
        session = kwargs.pop("session", None)
        method = kwargs.pop("method", None)
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
                link = link.send(method, *args, **kwargs)
                link.save()
                success.append(link.id)
            except DSResourceException as exc:
                log.debug(exc)
                link = exc.resource
                link.save()
                errors.append(link.id)
            # Prepare next request
            has_next_request = current_request = link.create_next_request()
            count += 1
        # Output results in simple type for json serialization
        return [success, errors]

    @staticmethod
    @app.task(name="HttpFetch.send_mass")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _send_mass(config, args_list, kwargs_list, session=None, method=None):
        # FEATURE: chain "batches" of fetch_mass if configured through batch_size

        if config.concat_args_size:
            # Set some vars based on config
            symbol = config.concat_args_symbol
            concat_size = config.concat_args_size
            args_list_size = int(len(args_list) / concat_size) + 1
            # Calculate new args_list and kwargs_list
            # Arg list that are of the form [[1],[2],[3], ...] should become [[1|2|3], ...]
            # Kwargs are assumed to remain similar across the list
            prc_args_list = []
            prc_kwargs_list = []
            for index in range(0, args_list_size):
                args_slice = args_list[index*concat_size:index*concat_size+concat_size]
                joined_slice = []
                for args in args_slice:
                    joined = symbol.join(map(str, args))
                    joined_slice.append(joined)
                prc_args_list.append([symbol.join(joined_slice)])
                prc_kwargs_list.append(kwargs_list[index*config.concat_args_size])
        else:
            prc_args_list = args_list
            prc_kwargs_list = kwargs_list

        return HttpResourceProcessor._send_serie(
            prc_args_list,
            prc_kwargs_list,
            config=config,
            method=method,
            session=session
        )

    @staticmethod
    @app.task(name="HttpFetch.send_serie")
    @load_config(defaults=DEFAULT_CONFIGURATION)
    def _send_serie(config, args_list, kwargs_list, session=None, method=None):
        success = []
        errors = []
        if session is None:
            session = requests.Session()
        for args, kwargs in zip(args_list, kwargs_list):
            # Get the results
            scc, err = HttpResourceProcessor._send(method=method, config=config, session=session, *args, **kwargs)
            success += scc
            errors += err
            # Take a break for scraping if configured
            interval_duration = config.interval_duration / 1000
            if interval_duration:
                sleep(interval_duration)
        return [success, errors]

    #######################################################
    # TASKS
    #######################################################
    # Wrappers that act as an interface
    # to background retrieval of resources

    @property
    def fetch(self):
        return self._send.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def fetch_mass(self):
        return self._send_mass.s(
            method="get",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def submit(self):
        return self._send.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def submit_mass(self):
        return self._send_mass.s(
            method="post",
            config=self.config.to_dict(private=True, protected=True)
        )

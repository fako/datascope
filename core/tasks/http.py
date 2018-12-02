import logging
from time import sleep

from celery import current_app as app

from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.base import Processor
from core.utils.configuration import ConfigurationType, load_config
from core.utils.helpers import get_any_model
from core.exceptions import DSResourceException


log = logging.getLogger("datascope")


def load_session():  # TODO: test to unlock
    """
    This decorator will try to fetch a session object based on the "session" keyword argument.
    If the argument is a string it is assumed to be the name of a processor that implements the get_session method.
    Whatever this method returns gets injected under the "session" keyword argument for the decorated function.
    If the argument is not a string it gets returned as being a valid session for the resource.

    :param defaults: (mixed) Name of the session provider or the session object.
    :return:
    """
    def wrap(func):
        def session_func(config, *args, **kwargs):
            assert isinstance(config, ConfigurationType), \
                "load_session expects a fully prepared ConfigurationType for config"
            session_injection = kwargs.pop("session", None)
            if not session_injection:
                raise TypeError("load_session decorator expects a session kwarg.")
            if not isinstance(session_injection, str):
                return func(config, session=session_injection, *args, **kwargs)
            session_provider = Processor.get_processor_class(session_injection)
            session = session_provider.get_session(config)
            return func(config, session=session, *args, **kwargs)
        return session_func
    return wrap


def get_resource_link(config, session=None):
    assert isinstance(config, ConfigurationType), \
        "get_resource_link expects a fully prepared ConfigurationType for config"
    Resource = get_any_model(config.resource)
    link = Resource(config=config.to_dict(protected=True))

    if session is not None:
        link.session = session
    assert link.session, "Http resources require a session object to get a link object."
    token = getattr(link.session, "token", None)
    if token:
        link.token = session.token
    # FEATURE: update session to use proxy when configured
    return link


@app.task(name="core.send")
@load_config(defaults=DEFAULT_CONFIGURATION)
@load_session()
def send(config, *args, **kwargs):
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
        link = get_resource_link(config, session)
        link.request = current_request
        try:
            link = link.send(method, *args, **kwargs)
            link.close()
            success.append(link.id)
        except DSResourceException as exc:
            log.debug(exc)
            link = exc.resource
            link.clean()
            link.save()
            errors.append(link.id)
        # Prepare next request
        has_next_request = current_request = link.create_next_request()
        count += 1
    # Output results in simple type for json serialization
    return [success, errors]


@app.task(name="core.send_serie")
@load_config(defaults=DEFAULT_CONFIGURATION)
@load_session()
def send_serie(config, args_list, kwargs_list, session=None, method=None):  # TODO: test to unlock
    success = []
    errors = []
    for args, kwargs in zip(args_list, kwargs_list):
        # Get the results
        scc, err = send(method=method, config=config, session=session, *args, **kwargs)
        success += scc
        errors += err
        # Take a break for scraping if configured
        interval_duration = config.interval_duration / 1000
        if interval_duration:
            sleep(interval_duration)
    return [success, errors]


@app.task(name="core.send_mass")
@load_config(defaults=DEFAULT_CONFIGURATION)
@load_session()
def send_mass(config, args_list, kwargs_list, session=None, method=None):
    # FEATURE: chain "batches" of send_mass if configured through batch_size

    assert args_list and kwargs_list, "No args list and/or kwargs list given to send mass"

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
            prc_kwargs_list.append(kwargs_list[0])
    else:
        prc_args_list = args_list
        prc_kwargs_list = kwargs_list

    return send_serie(
        prc_args_list,
        prc_kwargs_list,
        config=config,
        method=method,
        session=session
    )

import logging

from celery import current_app as app

from datascope.configuration import DEFAULT_CONFIGURATION
from core.utils.configuration import load_config
from core.utils.helpers import get_any_model
from core.exceptions import DSResourceException


log = logging.getLogger("datascope")


@app.task(name="core.run")
@load_config(defaults=DEFAULT_CONFIGURATION)
def run(config, *args, **kwargs):
    # Set vars
    success = []
    errors = []
    Resource = get_any_model(config.resource)
    cmd = Resource(config=config.to_dict(protected=True))
    # Run the command
    try:
        cmd = cmd.run(*args, **kwargs)
        cmd.clean()
        cmd.save()
        success.append(cmd.id)
    except DSResourceException as exc:
        log.debug(exc)
        cmd = exc.resource
        cmd.clean()
        cmd.save()
        errors.append(cmd.id)

    # Output results in simple type for json serialization
    return [success, errors]


@app.task(name="core.run_serie")
@load_config(defaults=DEFAULT_CONFIGURATION)
def run_serie(config, args_list, kwargs_list):
    success = []
    errors = []
    for args, kwargs in zip(args_list, kwargs_list):
        scc, err = run(config=config, *args, **kwargs)
        success += scc
        errors += err
    return [success, errors]

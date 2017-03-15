from time import sleep
import logging

import requests

from celery import current_app as app
from celery.result import AsyncResult, states as TaskStates

from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty, ConfigurationType, load_config
from core.utils.helpers import get_any_model
from core.exceptions import DSResourceException, DSProcessUnfinished, DSProcessError

log = logging.getLogger("datascope")


class ManifestProcessor(Processor):

    ARGS_BATCH_METHODS = ['manifest_batch']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="manifest_processor"
    )

    def manifest_from_individuals(self, individuals):
        print(self.config.to_dict(protected=True))
        for individual in individuals:
            print(individual)
            yield individual

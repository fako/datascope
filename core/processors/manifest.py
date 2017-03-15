from time import sleep
import logging

import requests

from celery import current_app as app
from celery.result import AsyncResult, states as TaskStates

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms import Individual
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

    def __init__(self, config):
        super(ManifestProcessor, self).__init__(config)
        assert "_community" in config or "community" in config, \
            "ManifestProcessor expects a community that it should manifest in the configuration."
        self._community = None

    @property
    def community(self):
        if not self._community:
            self._community = get_any_model(self.config.community)
        return self._community

    def manifest_from_individuals(self, individuals):
        from core.views.community import CommunityView  # TODO: move out of method
        from core.models.organisms.community import Manifestation
        for individual in individuals:
            args = Individual.output_from_content(individual, self.config.args)
            kwargs = Individual.output_from_content(individual, self.config.kwargs)
            signature = self.community.get_signature_from_input(*args, **kwargs)
            community_instance = self.community.objects.get_latest_by_signature(signature, **kwargs)
            community_path = CommunityView.get_full_path(self.community, "/".join(args), kwargs)
            manifestation = Manifestation(uri=community_path, community=community_instance)
            manifestation.save()
            manifestation.get_data()
            yield individual

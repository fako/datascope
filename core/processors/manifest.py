import logging

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.individual import Individual
from core.models.organisms.manifestation import Manifestation
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty
from core.utils.helpers import get_any_model
from core.views.community import CommunityView


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

from copy import deepcopy

from core.models.organisms import Individual
from core.processors.rank import LegacyRankProcessor


class ComparisonProcessor(LegacyRankProcessor):

    def __init__(self, config):
        super(ComparisonProcessor, self).__init__(config)
        assert "$reference" in config or "reference" in config or "_reference" in config, \
            "Expected a reference configuration to make comparisons with in ComparisonProcessor"
        self.reference = Individual.objects.get(id=int(self.config.reference))

    def get_hook_arguments(self, individual):
        return (deepcopy(individual), deepcopy(self.reference.properties),)

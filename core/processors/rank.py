from __future__ import unicode_literals, absolute_import, print_function, division
import six

from datascope.configuration import DEFAULT_CONFIGURATION
from core.utils.configuration import ConfigurationProperty


class RankProcessor(object):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="rank_processor"
    )

    def __init__(self, config):
        super(RankProcessor, self).__init__()
        assert isinstance(config, dict), "ExtractProcessor expects an objective to extract in the configuration."
        self.config = config

    def hooks(self, individuals):
        config_dict = self.config.to_dict()
        hooks = [
            getattr(self, hook[1:])
            for hook in six.iterkeys(config_dict)  # config gets whitelisted by Community
            if isinstance(hook, str) and hook.startswith("$") and callable(getattr(self, hook[1:], None))
        ]
        for hook in hooks:
            total = 0
            for individual in individuals:
                total += hook(individual)
            if not total:
                return individuals
            for individual in individuals:
                weight = hook(individual) / total * float(config_dict["$"+hook.__name__])
                if "ds_rank" not in individual:
                    individual["ds_rank"] = weight
                else:
                    individual["ds_rank"] *= weight
        return sorted(individuals, key=lambda el: el.get("ds_rank", 0), reverse=True)

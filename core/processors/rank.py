from __future__ import unicode_literals, absolute_import, print_function, division
import six

from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty


class RankProcessor(Processor):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="rank_processor"
    )

    def hooks(self, individuals):
        config_dict = self.config.to_dict()
        hooks = [
            getattr(self, hook[1:])
            for hook, weight in six.iteritems(config_dict)  # config gets whitelisted by Community
            if isinstance(hook, str) and hook.startswith("$") and callable(getattr(self, hook[1:], None)) and weight
        ]
        # TODO: There are problems with the memory consumption of this piece of code.
        # 1)   Give the kernel to "body" processor methods instead of the content. Make a default content reader processor
        # 2)   Make the content of collectives return a generator (use ( and ) instead of [ and ])
        # 3)   Use content for each hook to calculate the total (using reduce?) and write batches to numbered batch files in a folder with name: rank-<kernal_id>-<hooks>
        # 4)   If such a folder exists raise DuplicateProcessorInAction() and catch to return 202
        # 5)   Write "ranked" temp files that have ds_rank set
        # 6)   Read all ranked hook files as batches and combine the ratings in new tmp files that are sorted
        # 7)   Return an iterator over all combined files using heapq.merge
        # 8)   Make manifestations always work with iterators and use itertools.islice for wiki_news
        for hook in hooks:
            for individual in individuals:
                module_value = hook(individual)
                module_weight = float(config_dict["$"+hook.__name__])
                if not module_value:
                    continue
                if isinstance(module_value, bool):
                    module_value = int(module_value)
                if not isinstance(module_value, six.integer_types):
                    continue
                if "ds_rank" not in individual:
                    individual["ds_rank"] = module_value * module_weight
                else:
                    individual["ds_rank"] *= module_value * module_weight
        return sorted(individuals, key=lambda el: el.get("ds_rank", 0), reverse=True)

from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import reduce
import six

from itertools import islice

from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.base import Processor
from core.utils.configuration import ConfigurationProperty
from core.utils.helpers import merge_iter


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
        sort_key = lambda el: el["ds_rank"].get("rank", 0)
        results = []
        batch = []

        def flush_batch(batch, result_size):
            sorted_batch = sorted(batch, key=sort_key, reverse=True)[:result_size]
            results.append(sorted_batch)

        for idx, individual in enumerate(individuals):
            # Get ranks from modules
            individual["ds_rank"] = {hook.__name__: 0 for hook in hooks}
            for hook in hooks:
                hook_name = hook.__name__
                module_value = hook(individual)
                # TODO: assert hash equality
                module_weight = float(config_dict["$"+hook_name])
                if not module_value:
                    continue
                if isinstance(module_value, bool):
                    module_value = int(module_value)
                if not isinstance(module_value, six.integer_types):
                    continue
                individual["ds_rank"][hook_name] = module_value * module_weight
            # Aggregate all ranks to a single rank
            rankings = [ranking for ranking in six.itervalues(individual["ds_rank"]) if ranking]
            if rankings:
                individual["ds_rank"]["rank"] = reduce(lambda reduced, rank: reduced * rank, rankings, 1)
            else:
                individual["ds_rank"]["rank"] = 0
            # Write batch to results when appropriate
            if not idx % self.config.batch_size and len(batch):
                flush_batch(batch, self.config.result_size)
                batch = []
            # Append ranked individual to batch
            batch.append(individual)

        flush_batch(batch, self.config.result_size)
        return islice(merge_iter(*results, key=sort_key, reversed=True), self.config.result_size)

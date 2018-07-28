##################################################################
# START LEGACY
##################################################################
from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import reduce
import six

from itertools import islice
from copy import deepcopy

from core.utils.helpers import merge_iter


class LegacyRankProcessorMixin(object):

    def score(self, individuals):
        sort_key = lambda el: el.get(self.config.score_key, 0)
        results = []
        batch = []

        def flush_batch(batch, result_size):
            sorted_batch = sorted(batch, key=sort_key, reverse=True)[:result_size]
            results.append(sorted_batch)

        for idx, individual in enumerate(individuals):
            if not idx % self.config.batch_size and len(batch):
                flush_batch(batch, self.config.result_size)
                batch = []
            batch.append(individual)

        flush_batch(batch, self.config.result_size)
        return islice(merge_iter(*results, key=sort_key, reversed=True), self.config.result_size)

    def get_hook_arguments(self, individual):
        return (deepcopy(individual),)

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
            rank_info = {hook.__name__: {"rank": 0.0} for hook in hooks}
            for hook in hooks:
                hook_name = hook.__name__
                try:
                    hook_result = hook(*self.get_hook_arguments(individual))
                    module_value = float(hook_result)
                    module_weight = float(config_dict["$"+hook_name])
                except (ValueError, TypeError):
                    continue
                if module_value is None:
                    continue
                rank_info[hook_name] = {
                    "rank": module_value * module_weight,
                    "value": module_value,
                    "weight": module_weight
                }
            # Aggregate all ranks to a single rank
            hook_rankings = [ranking for ranking in six.itervalues(rank_info) if ranking["rank"]]
            if hook_rankings:
                rank_info["rank"] = reduce(
                    lambda reduced, hook_rank_info: reduced + hook_rank_info["rank"],
                    hook_rankings,
                    0
                )
            # Set info on individual and write batch to results when appropriate
            individual['ds_rank'] = rank_info
            if not idx % self.config.batch_size and len(batch):
                flush_batch(batch, self.config.result_size)
                batch = []
            # Append ranked individual to batch
            batch.append(individual)

        flush_batch(batch, self.config.result_size)
        return islice(merge_iter(*results, key=sort_key, reversed=True), self.config.result_size)
##################################################################
# END LEGACY
##################################################################


from datascope.configuration import DEFAULT_CONFIGURATION
from core.processors.base import Processor
from core.utils.data import NumericFeaturesFrame
from core.utils.configuration import ConfigurationProperty


class RankProcessor(Processor, LegacyRankProcessorMixin):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="rank_processor"
    )

    def __init__(self, config):
        super().__init__(config)
        if "identifier_key" in self.config and "load_feature_frame" in self.config:
            self.feature_frame = NumericFeaturesFrame(
                identifier=lambda ind: ind[self.config.identifier_key],
                features=self.get_features()
            )
        else:
            self.feature_frame = None

    @classmethod
    def get_features(cls):
        mother = set(dir(RankProcessor))
        own = set(dir(cls))
        return [getattr(cls, attr) for attr in (own - mother) if callable(getattr(cls, attr))]

    def ranking(self, descending=True, limit=20):
        assert self.feature_frame, \
            "RankProcessor needs a identifier_key and load_feature_frame configuration to perform RankProcessor.ranking"

##################################################################
# START LEGACY
##################################################################
from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import reduce
import six

import warnings
from collections import OrderedDict
from itertools import islice
from copy import deepcopy

from core.utils.helpers import merge_iter


class LegacyRankProcessorMixin(object):

    def score(self, individuals):
        warnings.warn("The RankProcessor.score method is deprecated. Use by_feature instead.", DeprecationWarning)
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
from core.utils.data import NumericFeaturesFrame, TextFeaturesFrame
from core.utils.configuration import ConfigurationProperty


class RankProcessor(Processor, LegacyRankProcessorMixin):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=[],
        namespace="rank_processor"
    )

    contextual_features = []

    def __init__(self, config):
        super().__init__(config)
        if "identifier_key" in self.config and "feature_frame_path" in self.config:
            self.feature_frame = NumericFeaturesFrame(
                identifier=lambda ind: ind[self.config.identifier_key],
                features=self.get_features(),
                file_path=self.config.feature_frame_path
            )
        else:
            self.feature_frame = None
        if "identifier_key" in self.config and "text_frame_path" in self.config:
            self.text_frame = TextFeaturesFrame(
                get_identifier=lambda ind: ind[self.config.identifier_key],
                get_text=self.get_text,
                file_path=self.config.text_frame_path
            )
        else:
            self.text_frame = None

    def get_text(self, document):
        raise NotImplementedError("The get_text method should be implemented in its context")

    @classmethod
    def get_features(cls):
        mother = set(dir(RankProcessor))
        own = set(dir(cls))
        return [
            getattr(cls, attr) for attr in (own - mother)
            if callable(getattr(cls, attr)) and
            attr not in cls.contextual_features
        ]

    def get_ranking_results(self, ranking, individuals, series):
        results = OrderedDict([(ix, None,) for ix in ranking.index])
        for individual in individuals:
            ix = individual[self.config.identifier_key]
            if ix not in results:
                continue
            individual["ds_rank"] = {
                "rank": ranking.at[ix]
            }
            for serie in series:
                individual["ds_rank"][serie.name] = {
                    "rank": serie.at[ix] ,  # TODO: rank value should be multiplied by weight
                    "value": serie.at[ix],
                    "weight": 1.0
                }
            results[ix] = individual
        return (value for value in results.values() if value is not None)

    def default_ranking(self, individuals):
        raise NotImplementedError("The default_ranking method should be implemented in its context")

    def by_feature(self, individuals):
        assert "ranking_feature" in self.config, "RankProcessor.by_feature needs a ranking_feature from config"
        assert self.feature_frame, \
            "RankProcessor needs a identifier_key and feature_frame_path configuration " \
            "to perform RankProcessor.by_feature"
        ranking_feature = self.config.ranking_feature
        assert ranking_feature in self.feature_frame.features or ranking_feature in self.contextual_features, \
            "The non-contextual feature '{}' is not loaded in the feature frame".format(ranking_feature)
        if ranking_feature not in self.contextual_features:
            ranked_feature = self.feature_frame.data[ranking_feature]
        else:
            # TODO: optimize memory use for contextual features or deprecate contextual features
            individuals = list(individuals)
            ranked_feature = self.feature_frame.get_feature_series(
                ranking_feature, getattr(self, ranking_feature),
                content_callable=lambda: individuals, context=self.config.to_dict()
            )
        ranked_feature = ranked_feature.sort_values(ascending=False)[:self.config.result_size]
        return self.get_ranking_results(ranked_feature, individuals, [ranked_feature])

    def by_params(self, individuals):
        pass

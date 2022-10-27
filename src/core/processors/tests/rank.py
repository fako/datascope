import os
from functools import reduce
from collections.abc import Iterator
from operator import itemgetter
from unittest.mock import patch, Mock

from django.test import TestCase
from django.db.models.query import QuerySet

from core.models import Individual
from core.utils.data import NumericFeaturesFrame
from core.tests.mocks.processor import MockRankProcessor, MockLegacyRankProcessor


class TestRankProcessorBase(TestCase):

    test_content = [
        {
            "name": "lowest",
            "value": 0
        },
        {
            "name": "lowest-2",
            "value": 0
        },
        {
            "name": "highest",
            "value": 10
        },
        {
            "name": "lowest-included",
            "value": 6
        },
        {
            "name": "not-included",
            "value": 1
        },
        {
            "name": "double-1",
            "value": 8
        },
        {
            "name": "under-double",
            "value": 7
        },
        {
            "name": "double-2",
            "value": 8
        },
        {
            "name": "highest-of-triple",
            "value": 9
        }
    ]

    def assert_rank_details(self, details, modules):
        rank_detail_keys = sorted(details.keys())
        expected_keys = sorted(modules + ['rank'])
        self.assertEqual(rank_detail_keys, expected_keys)
        rank = details.pop('rank')
        self.assertIsInstance(rank, float)
        for module, result in details.items():
            self.assertEqual(len(result.keys()), 3)
            self.assertEqual(result["rank"], result["weight"] * result["value"])
            for value in result.values():
                self.assertIsInstance(value, float)
        self.assertEqual(rank, reduce(lambda reduced, rank_info: reduced + rank_info["rank"], details.values(), 0))

    def assert_ranking(self, ranking, size, modules):
        ranking = list(ranking)
        self.assertEqual(len(ranking), 2)
        # Make sure that elements did not change except for added ranking
        for element in ranking:
            keys = sorted(element.keys())
            self.assertEqual(keys, ['_rank', 'name', 'value'])
        # Check structure of rank details separately
        rank_details = map(itemgetter('_rank'), ranking)
        for rank_detail in rank_details:
            self.assert_rank_details(rank_detail, modules)
        return ranking


class TestRankProcessor(TestRankProcessorBase):

    identifier_key = "name"
    frame_path = "test_rank_processor.pkl"
    blacklist_features = ["wrong_return_value", "i_think_none_of_it", "alter_individual"]

    @classmethod
    def setUpClass(cls):
        for forbidden_feature in cls.blacklist_features:
            setattr(cls, forbidden_feature, getattr(MockRankProcessor, forbidden_feature))
            setattr(MockRankProcessor, forbidden_feature, None)
        frame = NumericFeaturesFrame(
            lambda content: content[cls.identifier_key],
            MockRankProcessor.get_features(),
            lambda: cls.test_content
        )
        frame.to_disk(cls.frame_path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.frame_path)
        for forbidden_feature in cls.blacklist_features:
            setattr(MockRankProcessor, forbidden_feature, getattr(cls, forbidden_feature))

    def test_by_feature(self):
        instance = MockRankProcessor({
            "identifier_key": self.identifier_key,
            "feature_frame_path": self.frame_path,
            "ranking_feature": "rank_by_value",
            "result_size": 2
        })
        content_iterator = Mock(
            return_value=(
                Mock(
                    spec_set=Individual,
                    properties=content,
                    content=content,
                    identity=content[self.identifier_key],
                    __getitem__=Individual.__getitem__
                )
                for content in self.test_content
            )
        )
        query_set = Mock(
            spec_set=QuerySet,
            count=Mock(return_value=len(self.test_content)),
            iterator=content_iterator,
            filter=content_iterator
        )
        ranking = instance.by_feature(query_set)
        self.assertTrue(issubclass(ranking.__class__, Iterator))
        ranking = self.assert_ranking(ranking, 2, ['rank_by_value'])
        # Check order of results
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['highest', 'highest-of-triple'], "Order of ranked dictionaries is not correct.")
        self.skipTest("Rewrite with real query set instead of a mock")


class TestRankProcessorLegacy(TestRankProcessorBase):

    def test_ranking_with_score(self):
        self.skipTest("not tested")  # TODO: make sure that partial batches work

    def test_ranking_with_one_hook(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 1
        })
        ranking = instance.hooks(self.test_content)
        self.assertTrue(issubclass(ranking.__class__, Iterator))
        ranking = self.assert_ranking(ranking, 2, ['rank_by_value'])
        # Check order of results
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['highest', 'highest-of-triple'], "Order of ranked dictionaries is not correct.")

    def test_ranking_with_multiple_hooks(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 1,
            "$is_double": 5
        })
        ranking = instance.hooks(self.test_content)
        self.assertTrue(issubclass(ranking.__class__, Iterator))
        ranking = self.assert_ranking(ranking, 2, ['rank_by_value', 'is_double'])
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['double-1', 'double-2'], "Order of ranked dictionaries is not correct.")

    def test_floats_as_weights(self):
        instance = MockLegacyRankProcessor({
            "result_size": 3,
            "batch_size": 4,
            "$rank_by_value": 1,
            "$is_highest": 0.8
        })
        ranking = instance.hooks(self.test_content)
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['highest', 'highest-of-triple', 'double-1'], "Order of ranked dictionaries is not correct.")

    def test_negative_weights(self):
        instance = MockLegacyRankProcessor({
            "result_size": 3,
            "batch_size": 4,
            "$rank_by_value": 1,
            "$is_highest": -10
        })
        ranking = instance.hooks(self.test_content)
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['double-1', 'double-2', 'under-double'], "Order of ranked dictionaries is not correct.")

    def test_boolean_ranking(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$is_highest": 1
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['highest', 'highest-of-triple'], "Order of ranked dictionaries is not correct.")
        self.assertEqual(ranking[0]["_rank"]["rank"], ranking[1]["_rank"]["rank"])

    def test_no_hooks(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_not_existing_hooks(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$does_not_exist": 1
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_invalid_hook_name(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "rank_by_value": 1  # misses $
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_invalid_hook_weight(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": "makes no sense"
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_disabled_hook(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 0
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_wrong_hook_return_value(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$wrong_return_value": 1
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    def test_hook_none_value(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$i_think_none_of_it": 1
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['lowest', 'lowest-2'], "Order of ranked dictionaries is not correct.")

    @patch('core.processors.rank.islice')
    def test_order(self, islice_patch):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 1
        })
        instance.hooks(self.test_content)
        self.assertEqual(islice_patch.call_count, 1)
        args, kwargs = islice_patch.call_args
        order = list(args[0])
        order_keys = list(map(itemgetter('name'), order))
        self.assertEqual(
            order_keys,
            ['highest', 'highest-of-triple', 'double-1', 'double-2', 'lowest-included', 'lowest'],
            "Order of ranked dictionaries is not correct or splitting it batches did not work."
        )
        self.assertEqual(args[1], 2, "Slice should be the size of the result")

    def test_floats_as_values(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 1,
            "$ban_highest": 10
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['double-1', 'double-2'], "Order of ranked dictionaries is not correct.")

    def test_module_changing_individual(self):
        instance = MockLegacyRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$alter_individual": 1,
            "$rank_by_value": 1,
            "$ban_highest": 10
        })
        ranking = list(instance.hooks(self.test_content))
        names = list(map(itemgetter('name'), ranking))
        self.assertEqual(names, ['double-1', 'double-2'], "Order of ranked dictionaries is not correct.")

from __future__ import unicode_literals, absolute_import, print_function, division

from collections import Iterator
from operator import itemgetter

from mock import patch

from django.test import TestCase

from core.tests.mocks.processor import MockRankProcessor


class TestRankProcessor(TestCase):

    def setUp(self):
        self.test_content = [
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
        for key, value in details.items():
            self.assertIsInstance(value, float)
        rank_detail_keys = sorted(details.keys())
        expected_keys = sorted(modules + ['rank'])
        self.assertEqual(rank_detail_keys, expected_keys)
        rank = details.pop('rank')
        self.assertEqual(rank, sum(details.values()))

    def assert_ranking(self, ranking, size, modules):
        ranking = list(ranking)
        self.assertEqual(len(ranking), 2)
        # Make sure that elements did not change except for added ranking
        for element in ranking:
            keys = sorted(element.keys())
            self.assertEqual(keys, ['ds_rank', 'name', 'value'])
        # Check structure of rank details separately
        rank_details = map(itemgetter('ds_rank'), ranking)
        for rank_detail in rank_details:
            self.assert_rank_details(rank_detail, modules)
        return ranking

    def test_ranking_with_one_hook(self):
        instance = MockRankProcessor({
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
        self.skipTest("not tested")

    def test_floats_as_weights(self):
        self.skipTest("not tested")

    def test_boolean_ranking(self):
        self.skipTest("not tested")

    def test_invalid_hooks(self):
        self.skipTest("not tested")

    @patch('core.processors.rank.islice')
    def test_order(self, islice_patch):
        instance = MockRankProcessor({
            "result_size": 2,
            "batch_size": 3,
            "$rank_by_value": 1
        })
        instance.hooks(self.test_content)
        islice_patch.assert_called_once()
        args, kwargs = islice_patch.call_args
        order = list(args[0])
        order_keys = list(map(itemgetter('name'), order))
        self.assertEqual(
            order_keys,
            ['highest', 'highest-of-triple', 'double-1', 'double-2', 'lowest-included', 'lowest'],
            "Order of ranked dictionaries is not correct or splitting it batches did not work."
        )
        self.assertEqual(args[1], 2, "Slice should be the size of the result")

    ########################################
    # NOT IMPLEMENTED
    ########################################

    def test_floats_as_values(self):
        self.skipTest("not tested")

    def test_rejected_ranking(self):
        self.skipTest("not tested")

    def test_verbal_ranking(self):
        self.skipTest("not tested, test that value, weight and fail rate get returned as part of module rankings")

    def test_module_changing_individual(self):
        self.skipTest("not tested")

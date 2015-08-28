from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.models.organisms import Collective


class TestCollective(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollective, self).setUp()
        self.instance = Collective.objects.get(id=1)
        self.value_outcome = ["nested value 0", "nested value 1", "nested value 2"]
        self.list_outcome = [["nested value 0"], ["nested value 1"], ["nested value 2"]]
        self.double_list_outcome = [["nested value 0", "nested value 0"], ["nested value 1", "nested value 1"], ["nested value 2", "nested value 2"]]
        self.dict_outcome = [{"value": "nested value 0"}, {"value": "nested value 1"}, {"value": "nested value 2"}]

    def test_url(self):
        self.skipTest("not tested")

    def test_validate(self):
        self.skipTest("not tested")

    def test_update(self):
        self.skipTest("not tested")

    def test_output(self):
        results = self.instance.output("$.value")
        self.assertEqual(results, self.value_outcome)
        results = self.instance.output("$.value", "$.value")
        self.assertEqual(results, [self.value_outcome, self.value_outcome])
        results = self.instance.output(["$.value"])
        self.assertEqual(results, self.list_outcome)
        results = self.instance.output(["$.value", "$.value"])
        self.assertEqual(results, self.double_list_outcome)
        results = self.instance.output([])
        self.assertEqual(results, [[], [], []])
        results = self.instance.output({"value": "$.value"})
        self.assertEqual(results, self.dict_outcome)
        results = self.instance.output({})
        self.assertEqual(results, [{}, {}, {}])

    def test_json_content(self):
        self.skipTest("not tested")

    def test_group_by(self):
        self.skipTest("not tested")

    def test_get_index_keys(self):
        self.skipTest("not tested")

    def test_set_index_for_individual(self):
        self.skipTest("not tested")

    def test_influence(self):
        self.skipTest("not tested")

    def test_select(self):
        self.skipTest("not tested")

    def test_build_index(self):
        self.skipTest("not tested")

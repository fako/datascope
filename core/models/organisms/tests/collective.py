from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.models.organisms import Collective


class TestCollective(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollective, self).setUp()
        self.instance = Collective.objects.get(id=1)
        self.value_outcome = ["nested value 0", "nested value 1", "nested value 2"]
        self.dict_outcome = [{"value": "nested value 0"}, {"value": "nested value 1"}, {"value": "nested value 2"}]

    def test_output(self):
        results = self.instance.output("$.value")
        self.assertEqual(results, self.value_outcome)
        results = self.instance.output("$.value", "$.value")
        self.assertEqual(results, [self.value_outcome, self.value_outcome])
        results = self.instance.output(["$.value"])
        self.assertEqual(results, self.value_outcome)
        results = self.instance.output(["$.value", "$.value"])
        self.assertEqual(results, [self.value_outcome, self.value_outcome])
        results = self.instance.output([])
        self.assertEqual(results, [[], [], []])
        results = self.instance.output({"value": "$.value"})
        self.assertEqual(results, self.dict_outcome)
        results = self.instance.output([{"value": "$.value"}, {"value": "$.value"}])
        self.assertEqual(results, [self.dict_outcome, self.dict_outcome])
        results = self.instance.output({})
        self.assertEqual(results, [{}, {}, {}])

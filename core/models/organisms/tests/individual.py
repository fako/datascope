from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.models.organisms import Individual


class TestIndividual(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestIndividual, self).setUp()
        self.instance = Individual.objects.get(id=1)
        self.value_outcome = "nested value 0"
        self.dict_outcome = {"value": "nested value 0"}

    def test_output(self):
        results = self.instance.output("$.value")
        self.assertEqual(results, self.value_outcome)
        results = self.instance.output("$.value", "$.value")
        self.assertEqual(list(results), [self.value_outcome, self.value_outcome])
        results = self.instance.output(["$.value"])
        self.assertEqual(results, [self.value_outcome])
        results = self.instance.output(["$.value", "$.value"])
        self.assertEqual(list(results), [self.value_outcome, self.value_outcome])
        results = self.instance.output([])
        self.assertEqual(results, [])
        results = self.instance.output({"value": "$.value"})
        self.assertEqual(results, self.dict_outcome)
        results = self.instance.output([{"value": "$.value"}, {"value": "$.value"}])
        self.assertEqual(list(results), [self.dict_outcome, self.dict_outcome])
        results = self.instance.output({})
        self.assertEqual(results, {})

    def test_update(self):
        self.skipTest("not tested")

    def test_validate(self):
        self.skipTest("not tested")

    def test_clean(self):
        self.skipTest("not tested")

    def test_json_content(self):
        self.skipTest("not tested")

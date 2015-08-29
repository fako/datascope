from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TransactionTestCase, TestCase
from django.db.models.query import QuerySet

from core.models.organisms import Collective, Individual


class TestCollective(TransactionTestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollective, self).setUp()
        self.instance = Collective.objects.get(id=1)
        self.instance2 = Collective.objects.get(id=2)
        self.individual = Individual.objects.get(id=4)
        self.value_outcome = ["nested value 0", "nested value 1", "nested value 2"]
        self.list_outcome = [["nested value 0"], ["nested value 1"], ["nested value 2"]]
        self.double_list_outcome = [["nested value 0", "nested value 0"], ["nested value 1", "nested value 1"], ["nested value 2", "nested value 2"]]
        self.dict_outcome = [{"value": "nested value 0"}, {"value": "nested value 1"}, {"value": "nested value 2"}]

    def test_url(self):
        self.skipTest("not tested")

    def test_validate(self):
        self.skipTest("not tested")

    # TODO: patch validate and assert it being used or not
    # TODO: patch influence and assert it is being used
    def test_update(self):
        updates = []
        for index, individual in enumerate(self.instance2.individual_set.all()):
            individual.properties["value"] = 3
            updates.append(individual) if index % 2 else updates.append(individual.properties)
        with self.assertNumQueries(6):
            self.instance2.update(updates, validate=False)
        values = [
            ind.properties["value"] for ind in
            self.instance2.individual_set.all()
        ]
        self.assertEqual(len(values), 5)
        map(lambda v: self.assertEqual(v, 3), values)

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

    def test_set_index_for_individual(self):
        individual = self.instance2.set_index_for_individual(self.individual, ["language"])
        self.assertEqual(
            self.instance2.indexes,
            {
                (("language", "nl",),): 0,
            }
        )
        self.assertEqual(individual.index, 0)

    def test_influence(self):
        self.skipTest("not tested")

    def test_select(self):
        self.instance2.build_index(["language", "country"])
        qs = self.instance2.select(country="NL")
        self.assertIsInstance(qs, QuerySet)
        words = [ind["word"] for ind in qs.all()]
        self.assertEqual(words, ["pensioen", "ouderdom"])
        qs = self.instance2.select(language="nl")
        self.assertIsInstance(qs, QuerySet)
        words = [ind["word"] for ind in qs.all()]
        self.assertEqual(words, ["pensioen", "ouderdom", "pensioen"])
        self.skipTest(
            "Make sure that QuerySet gets re-used through: "
            "https://docs.djangoproject.com/en/dev/topics/testing/tools/#django.test.TransactionTestCase.assertNumQueries"
        )

    def test_build_index(self):
        self.instance2.build_index(["language", "country"])
        self.assertEqual(
            self.instance2.indexes,
            {
                (("language", "nl",), ("country", "NL",),): 0,
                (("language", "nl",), ("country", "BE",),): 1,
                (("language", "en",), ("country", "GB",),): 2,
            }
        )
        individual = Individual.objects.last()
        self.assertEqual(individual.index, 2)

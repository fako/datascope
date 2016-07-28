from __future__ import unicode_literals, absolute_import, print_function, division

from mock import patch

from django.test import TransactionTestCase
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

    def get_update_list_and_ids(self, value):
        updates = []
        individual_ids = []
        for index, individual in enumerate(self.instance2.individual_set.all()):
            individual_ids.append(individual.id)
            individual.properties["value"] = value
            updates.append(individual) if index % 2 else updates.append(individual.properties)
        return updates, individual_ids

    @patch('core.models.organisms.collective.Individual.validate')
    @patch('core.models.organisms.collective.Collective.influence')
    def test_update(self, influence_method, validate_method):
        updates, individual_ids = self.get_update_list_and_ids(value="value 3")
        with self.assertNumQueries(3):
            # Query 1: reset
            # Query 2: fetch community to set it for pure dicts becoming Individuals
            # Query 3: insert individuals
            self.instance2.update(updates, validate=False, reset=True)
        validate_method.assert_not_called()
        self.assertEqual(influence_method.call_count, 5)
        self.assertEqual(self.instance2.individual_set.count(), 5)
        for individual in self.instance2.individual_set.all():
            self.assertEqual(individual.properties["value"], "value 3")
            self.assertNotIn(individual.id, individual_ids)

        influence_method.reset_mock()
        updates, individual_ids = self.get_update_list_and_ids(value="value 4")
        with self.assertNumQueries(2):
            # Query 1: reset
            # NB: no need to fetch community as this has been done
            # Query 2: insert individuals
            self.instance2.update(updates, validate=True, reset=True)
        self.assertEqual(validate_method.call_count, 5)
        self.assertEqual(influence_method.call_count, 5)
        self.assertEqual(self.instance2.individual_set.count(), 5)
        for individual in self.instance2.individual_set.all():
            self.assertEqual(individual.properties["value"], "value 4")
            self.assertNotIn(individual.id, individual_ids)

        influence_method.reset_mock()
        updates, individual_ids = self.get_update_list_and_ids(value="value 5")
        with self.assertNumQueries(1):  # query set cache is filled, -1 query
            # NB: no reset
            # NB: no need to fetch community as this has been done
            # Query 1: insert individuals
            self.instance2.update(updates, validate=True, reset=False)
        self.assertEqual(validate_method.call_count, 10)
        self.assertEqual(influence_method.call_count, 5)
        self.assertEqual(self.instance2.individual_set.count(), 10)
        new_ids = []
        for individual in self.instance2.individual_set.all():
            self.assertIn(individual.properties["value"], ["value 4", "value 5"])
            new_ids.append(individual.id)
        for id_value in individual_ids:
            self.assertIn(id_value, new_ids)

    def test_update_batch(self):
        updates = list(self.instance2.individual_set.all()) * 5
        with self.assertNumQueries(3):
            self.instance2.update(updates, validate=False, reset=True, batch_size=20)
        self.assertEqual(self.instance2.individual_set.count(), 25)

    def test_copy_update(self):
        self.skipTest("test that updating with Individuals from other Collective will copy Individuals")

    def test_output(self):
        results = self.instance.output("$.value")
        self.assertEqual(results, self.value_outcome)
        results = self.instance.output("$.value", "$.value")
        self.assertEqual(list(results), [self.value_outcome, self.value_outcome])
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

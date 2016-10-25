from __future__ import unicode_literals, absolute_import, print_function, division

from json import loads
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
        self.expected_content = [
            {"context": "nested value", "value": "nested value 0"},
            {"context": "nested value", "value": "nested value 1"},
            {"context": "nested value", "value": "nested value 2"}
        ]

    def test_url(self):
        url = self.instance.url
        self.assertEqual(url, '/data/v1/collective/1/content/')
        self.instance.id = None
        try:
            url = self.instance.url
            self.fail("url property did not raise when id is not known")
        except ValueError:
            pass

    @patch('core.models.organisms.collective.Individual.validate')
    def test_validate_queryset(self, validate_method):
        self.instance.validate(self.instance.individual_set.all(), self.instance.schema)
        for ind in self.instance.individual_set.all():
            validate_method.assert_any_call(ind, self.instance.schema)

    @patch('core.models.organisms.collective.Individual.validate')
    def test_validate_content(self, validate_method):
        self.instance.validate(self.instance.content, self.instance.schema)
        for ind in self.instance.content:
            validate_method.assert_any_call(ind, self.instance.schema)

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

    @patch('core.models.organisms.collective.Collective.influence')
    def test_copy_update(self, influence_method):
        updates, original_ids = self.get_update_list_and_ids("copy")
        self.instance.update(updates, validate=False, reset=False)
        self.assertEqual(self.instance.individual_set.count(), 8)
        for ind in self.instance.individual_set.all():
            self.assertNotIn(ind.id, original_ids)
        self.assertEqual(self.instance.individual_set.exclude(pk__in=[1, 2, 3]).count(), len(original_ids))
        for args, kwargs in influence_method.call_args_list:
            self.assertEqual(len(args), 1)
            self.assertIsInstance(args[0], Individual)
            self.assertEqual(kwargs, {})
        self.assertEqual(
            influence_method.call_count, len(original_ids),
            "Collective should only influence new Individuals when updating"
        )

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
        with patch('json.loads', return_value=[]) as json_loads:
            json_content = self.instance.json_content
            json_loads.assert_not_called()
        content = loads(json_content)
        self.assertEqual(
            content, self.expected_content,
            "JSON content did not meet expectation. Is get_json inside json_field.fields patched properly??"
        )

    def test_group_by(self):
        groups = self.instance2.group_by("country")
        for country, individuals in groups.items():
            for individual in individuals:
                self.assertEqual(individual.properties["country"], country)

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
        self.individual.identity = None
        self.instance2.influence(self.individual)
        self.assertEqual(self.individual.identity, self.individual.properties["word"])
        self.instance2.identifier = "country"
        self.instance2.influence(self.individual)
        self.assertEqual(self.individual.identity, self.individual.properties["country"])
        self.instance2.identifier = None
        self.instance2.influence(self.individual)
        self.assertEqual(self.individual.identity, self.individual.properties["country"])
        self.instance2.identifier = "does-not-exist"
        self.instance2.influence(self.individual)
        self.assertIsNone(self.individual.identity)

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

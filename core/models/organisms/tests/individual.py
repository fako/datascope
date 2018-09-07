from __future__ import unicode_literals, absolute_import, print_function, division

from mock import patch
from json import loads

from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models.organisms import Individual


class TestIndividual(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestIndividual, self).setUp()
        self.instance = Individual.objects.get(id=1)
        self.value_outcome = "nested value 0"
        self.dict_outcome = {"value": "nested value 0"}
        self.expected_content = {
            'value': 'nested value 0',
            'context': 'nested value'
        }
        self.expected_items = sorted([('context', 'nested value'), ('value', 'nested value 0')])

    def test_url(self):
        url = self.instance.url
        self.assertEqual(url, '/data/v1/individual/1/content/')
        self.instance.id = None
        try:
            url = self.instance.url
            self.fail("url property did not raise when id is not known")
        except ValueError:
            pass

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
        self.skipTest("Refactor to output_from_content")

    def test_update(self):
        self.skipTest("not tested")

    @patch("jsonschema.validate")
    def test_validate(self, jsonschema_validate):
        Individual.validate(self.instance, self.instance.schema)
        jsonschema_validate.assert_called_with(self.instance.properties, self.instance.schema)
        jsonschema_validate.reset_mock()
        Individual.validate(self.instance.properties, self.instance.schema)
        jsonschema_validate.assert_called_with(self.instance.properties, self.instance.schema)
        jsonschema_validate.reset_mock()
        Individual.validate(self.instance.content, self.instance.schema)
        jsonschema_validate.assert_called_with(self.instance.properties, self.instance.schema)
        jsonschema_validate.reset_mock()
        try:
            Individual.validate([self.instance], self.instance.schema)
        except ValidationError:
            jsonschema_validate.assert_not_called()

    def test_validate_error(self):
        wrong_content = self.instance.content
        wrong_content["wrong"] = True
        try:
            Individual.validate(wrong_content, self.instance.schema)
            self.fail("Individual.validate did not raise upon wrong content")
        except ValidationError:
            pass
        Individual.validate(wrong_content, {"bullshit": "schema"})  # TODO: assert schema?

    @patch('core.models.organisms.collective.Collective.influence')
    def test_clean_without_collective(self, influence_method):
        self.instance.collective = None
        self.instance.clean()
        influence_method.assert_not_called()

    @patch('core.models.organisms.collective.Collective.influence')
    def test_clean_with_collective(self, influence_method):
        self.instance.clean()
        influence_method.assert_called_once_with(self.instance)

    def test_json_content(self):
        with patch('json.loads', return_value=[]) as json_loads:
            json_content = self.instance.json_content
            json_loads.assert_not_called()
        content = loads(json_content)
        self.assertEqual(
            content, self.expected_content,
            "JSON content did not meet expectation. Is get_json inside json_field.fields patched properly??"
        )

    def test_getitem(self):
        value = self.instance["value"]
        self.assertEqual(value, self.instance.properties["value"])

    def test_setitem(self):
        self.instance["value"] = "new value"
        self.assertEqual(self.instance.properties["value"], "new value")

    def test_items(self):
        items = sorted(list(self.instance.items()))
        self.assertEqual(items, self.expected_items)

    def test_keys(self):
        expected_keys, expected_values = zip(*self.expected_items)
        keys = tuple(sorted(self.instance.keys()))
        self.assertEqual(keys, expected_keys)

    def test_values(self):
        expected_keys, expected_values = zip(*self.expected_items)
        values = tuple(sorted(self.instance.values()))
        self.assertEqual(values, expected_values)

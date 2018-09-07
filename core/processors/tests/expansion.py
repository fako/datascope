from django.test import TestCase

from core.models.organisms import Individual
from core.processors import ExpansionProcessor


class TestExpansionProcessor(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        self.individual_content = {
            "individual": "content",
            "expand": "/data/v1/collective/1/content/"
        }
        self.individual = Individual(properties={
            "individual": "instance",
            "expand": "/data/v1/collective/1/"
        })
        self.expected_content_expansion = {
            "individual": "content",
            "expand": [
                {
                    "_id": index + 1,
                    "value": "nested value {}".format(index),
                    "context": "nested value"
                }
                for index in range(3)
            ]
        }
        self.expected_instance_expansion = {
            "individual": "instance",
            "expand": [
                {
                    "_id": index + 1,
                    "value": "nested value {}".format(index),
                    "context": "nested value"
                }
                for index in range(3)
            ]
        }

    def test_collective_content_list(self):
        processor = ExpansionProcessor(config={})
        generator = processor.collective_content([self.individual_content, self.individual])
        test_content, test_individual = list(generator)
        self.assertIsInstance(test_content, dict)
        self.assertEqual(test_content, self.expected_content_expansion)
        self.assertIsInstance(test_individual, Individual)
        self.assertEqual(test_individual.properties, self.expected_instance_expansion)

    def test_collective_content_iterator(self):
        processor = ExpansionProcessor(config={})
        generator = processor.collective_content(
            iter([self.individual_content, self.individual])
        )
        test_content, test_individual = list(generator)
        self.assertIsInstance(test_content, dict)
        self.assertEqual(test_content, self.expected_content_expansion)
        self.assertIsInstance(test_individual, Individual)
        self.assertEqual(test_individual.properties, self.expected_instance_expansion)

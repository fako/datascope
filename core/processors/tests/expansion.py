from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.models.organisms import Individual
from core.processors import ExpansionProcessor


class TestExpansionProcessor(TestCase):

    fixtures = ["test-organisms"]
    expected_content_expansion = {
        "individual": "content",
        "expand": [
            {
                "value": "nested value {}".format(index),
                "context": "nested value"
            }
            for index in range(3)
        ]
    }
    expected_instance_expansion = {
        "individual": "instance",
        "expand": [
            {
                "value": "nested value {}".format(index),
                "context": "nested value"
            }
            for index in range(3)
        ]
    }

    def test_collective_content(self):
        individual_content = {
            "individual": "content",
            "expand": "/data/v1/collective/1/content/"
        }
        individual = Individual(properties={
            "individual": "instance",
            "expand": "/data/v1/collective/1/"
        })
        processor = ExpansionProcessor(config={})
        generator = processor.collective_content([individual_content, individual])
        test_content, test_individual = list(generator)
        self.assertIsInstance(test_content, dict)
        self.assertEqual(test_content, self.expected_content_expansion)
        self.assertIsInstance(test_individual, Individual)
        self.assertEqual(test_individual.properties, self.expected_instance_expansion)

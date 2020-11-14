from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.processors.compare import ComparisonProcessor
from core.models import Individual


class TestCompareProcessor(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super().setUp()
        self.prc = ComparisonProcessor(config={"reference": "1"})

    def test_init(self):
        prc = ComparisonProcessor(config={"reference": 1})
        self.assertIsInstance(prc, ComparisonProcessor)
        try:
            ComparisonProcessor(config={"reference": "100"})
            self.fail("CompareProccessor should not init with non-existing references")
        except Individual.DoesNotExist:
            pass
        try:
            ComparisonProcessor(config={"reference": "bull"})
            self.fail("CompareProccessor should not init with non-id values for reference")
        except ValueError:
            pass

    def test_get_hook_arguments(self):
        ind = Individual.objects.get(id=2)
        args = self.prc.get_hook_arguments(ind.properties)
        self.assertEqual(args, (ind.properties, self.prc.reference.properties))
        ind.properties["context"] = "changed"
        self.prc.reference.properties["context"] = "changed"
        for arg in args:
            self.assertEqual(arg["context"], "nested value")

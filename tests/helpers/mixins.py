from django.test import TestCase
from HIF.helpers.mixins import DataMixin


class MockDataMixin(DataMixin):
    @property
    def source(self):
        return [{
            "key": "right",
            "test": "test"
        },
        {
            "key": "right",
            "test": "test"
        },
        {
            "key": "wrong",
            "test": "test"
        }]


def test_cleaner(result_instance):
    if "wrong" in result_instance.values():
        return False
    else:
        return True


class TestDataMixin(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.translations = {
            "test": "translated"
        }

    def setUp(self):
        self.mixin = MockDataMixin()

    def test_results(self):
        results = self.mixin.results
        self.assertIsInstance(results,list)
        self.assertEqual(len(results),3)
        for result in results:
            self.assertIn("test",result)
            self.assertNotIn("translated",result)

    def test_translate_results_method(self):
        self.mixin._translations = self.translations
        results = self.mixin.results
        self.assertIsInstance(results,list)
        self.assertEqual(len(results),3)
        for result in results:
            self.assertIn("translated",result)
            self.assertNotIn("test",result)

    def test_cleaner_method(self):
        self.mixin.cleaner = test_cleaner
        results = self.mixin.results
        self.assertIsInstance(results,list)
        self.assertEqual(len(results),2)





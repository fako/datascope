from django.test import TestCase
from HIF.helpers.mixins import DataMixin, ConfigMixin


class MockDataMixin(DataMixin):
    @property
    def data_source(self):
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
        data = self.mixin.data
        self.assertIsInstance(data,list)
        self.assertEqual(len(data),3)
        for obj in data:
            self.assertIn("test",obj)
            self.assertNotIn("translated",obj)

    def test_translate_results_method(self):
        self.mixin.HIF_translations = self.translations
        data = self.mixin.data
        self.assertIsInstance(data,list)
        self.assertEqual(len(data),3)
        for obj in data:
            self.assertIn("translated",obj)
            self.assertNotIn("test",obj)

    def test_cleaner_method(self):
        self.mixin.cleaner = test_cleaner
        data = self.mixin.data
        self.assertIsInstance(data,list)
        self.assertEqual(len(data),2)


class MockConfigMixin(ConfigMixin):
    HIF_namespace = 'test'
    HIF_private = ['_test']

class TestConfigMixin(TestCase):
    pass


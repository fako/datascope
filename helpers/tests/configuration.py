from django.test import TestCase

# from mock import Mock

from HIF.models.storage import Storage, TextStorage
from HIF.helpers.configuration import Config, Domain
from HIF.helpers.storage import Container
from HIF.exceptions import HIFCouldNotLoadFromStorage

class MockDomain(object):
    TEST_namespace = "namespace"

class TestConfiguration(TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        #cls.config = Config()

    def test_config_init(self):
        # Standard init
        instance = Config(namespace="TEST",private=[])
        self.assertIsInstance(instance._domain, Domain)
        self.assertEqual(instance._namespace, "TEST")
        self.assertEqual(instance._private, Config._private)
        # Init with extra private fields
        instance = Config(namespace="TEST",private=["_test"])
        self.assertEqual(instance._private, Config._private + ["_test"])

    def test_config_access(self):
        instance = Config(namespace="TEST",private=[])
        instance({"test": "test"})
        self.assertTrue(hasattr(instance, "test"))
        self.assertEqual(instance.test, "test")

    def test_config_namespace(self):
        instance = Config(namespace="TEST", private=[])
        instance({"test": "test"})
        instance._domain = MockDomain()
        self.assertFalse(hasattr(instance, "namespace"))
        self.assertEqual(instance.namespace, "namespace")
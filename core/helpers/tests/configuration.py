from django.test import TestCase

from mock import Mock

from HIF.models.storage import Storage, TextStorage
from HIF.helpers.configuration import Config, Domain
from HIF.helpers.storage import Container
from HIF.exceptions import HIFCouldNotLoadFromStorage

class MockDomain(object):
    TEST_namespacing = "namespace"

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
        self.assertEqual(instance._private, Config._private_defaults)
        # Init with extra private fields
        instance = Config(namespace="TEST",private=["_namespace", "_test"])
        self.assertEqual(instance._private, Config._private_defaults + ["_test"])

    def test_config_access(self):
        instance = Config(namespace="TEST",private=[])
        instance({"test": "test"})
        self.assertTrue(hasattr(instance, "test"))
        self.assertEqual(instance.test, "test")

    def test_config_namespace(self):
        instance = Config(namespace="TEST", private=[])
        instance({"test": "test"})
        instance._domain = MockDomain()
        self.assertFalse("namespacing" in instance.__dict__)
        self.assertEqual(instance.namespacing, "namespace")

    def test_config_dict(self):
        instance = Config(namespace="TEST", private=['_test_private'])
        instance({
            "_test_private": "private",
            "_test_protected": "protected",
            "test_public": "public"
        })
        instance._domain = MockDomain()
        private = instance.dict(private=True)
        protected = instance.dict(protected=True)
        public = instance.dict()
        everything = instance.dict(private=True, protected=True)

        self.assertIn("_test_private", private)
        self.assertIn("test_public", private)
        self.assertNotIn("_test_protected", private)
        self.assertIn("_test_protected", protected)
        self.assertIn("test_public", protected)
        self.assertNotIn("_test_private", protected)
        self.assertIn("test_public", public)
        self.assertNotIn("_test_private", public)
        self.assertNotIn("_test_protected", public)
        self.assertIn("test_public", everything)
        self.assertIn("_test_private", everything)
        self.assertIn("_test_protected", everything)

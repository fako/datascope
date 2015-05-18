from django.test import TestCase

from datascope.configuration import MOCK_CONFIGURATION
from core.utils.configuration import ConfigurationType, ConfigurationNotFoundError, ConfigurationProperty


class TestConfigurationType(TestCase):

    def setUp(self):
        self.config = ConfigurationType(namespace="name", private=["_test3"], defaults=MOCK_CONFIGURATION)
        self.config.set_configuration({
            "test": "public",
            "_test2": "protected",
            "_test3": "private"
        })

    def test_init(self):
        # Implicit init
        instance = ConfigurationType(defaults=MOCK_CONFIGURATION)
        self.assertEqual(instance._defaults, MOCK_CONFIGURATION)
        self.assertEqual(instance._namespace, ConfigurationType._global_prefix)
        self.assertEqual(instance._private, ConfigurationType._private_defaults)
        # Explicit init with double private key
        instance = ConfigurationType(namespace="name", private=["_test", "_test", "oops"], defaults=MOCK_CONFIGURATION)
        self.assertEqual(instance._defaults, MOCK_CONFIGURATION)
        self.assertEqual(instance._namespace, "name")
        self.assertEqual(instance._private, ConfigurationType._private_defaults + ["_test", "_oops"])

    def test_attribute_access(self):
        self.assertEqual(self.config.test, "public")
        self.assertEqual(self.config.test2, "protected")
        self.assertEqual(self.config.test3, "private")
        # Not found error
        try:
            self.test = self.config.test4
            self.fail("ConfigurationType should raise an exception when configuration is not available")
        except ConfigurationNotFoundError:
            pass
        # Namespace configuration
        self.assertNotIn("namespace_configuration", self.config.__dict__)
        self.assertEqual(self.config.namespace_configuration, "namespace configuration")
        try:
            self.test = self.config.namespace_missing
            self.fail("ConfigurationType should raise an exception when namespace configuration is not available")
        except ConfigurationNotFoundError:
            pass
        # Global configuration
        self.assertNotIn("global_configuration", self.config.__dict__)
        self.assertEqual(self.config.global_configuration, "global configuration")
        try:
            self.test = self.config.namespace_missing
            self.fail("ConfigurationType should raise an exception when global configuration is not available")
        except ConfigurationNotFoundError:
            pass

    def test_update_using_set_configuration(self):
        self.config.set_configuration({"test": "public 2"})
        self.assertEqual(self.config.test, "public 2")
        self.assertEqual(self.config.test2, "protected")
        self.assertEqual(self.config.test3, "private")
        self.config.set_configuration({"_test2": "protected 2", "_test3": "private 2"})
        self.assertEqual(self.config.test, "public 2")
        self.assertEqual(self.config.test2, "protected 2")
        self.assertEqual(self.config.test3, "private 2")

    def test_to_dict(self):
        # Get all different possibilities
        private = self.config.to_dict(private=True)
        protected = self.config.to_dict(protected=True)
        public = self.config.to_dict()
        everything = self.config.to_dict(private=True, protected=True)
        # Check properties
        self.assertIn("_test3", private)
        self.assertIn("test", private)
        self.assertNotIn("_test2", private)
        self.assertIn("_test2", protected)
        self.assertIn("test", protected)
        self.assertNotIn("_test3", protected)
        self.assertIn("test", public)
        self.assertNotIn("_test2", public)
        self.assertNotIn("_test3", public)
        self.assertIn("test", everything)
        self.assertIn("_test2", everything)
        self.assertIn("_test3", everything)
        # Make sure that all private keys are there
        # But the defaults key should not be passed down
        self.assertEqual(len(self.config._private) - 1 + len(public), len(private))

    def test_from_dict(self):
        type_instance = ConfigurationType.from_dict(
            self.config.to_dict(private=True, protected=True),
            MOCK_CONFIGURATION
        )
        self.assertEqual(type_instance.test, "public")
        self.assertEqual(type_instance.test2, "protected")
        self.assertEqual(type_instance.test3, "private")
        self.assertEqual(type_instance.global_configuration, "global configuration")
        self.assertEqual(type_instance.namespace_configuration, "namespace configuration")
        self.assertEqual(type_instance._private, self.config._private)


class TestConfigurationProperty(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestConfigurationProperty, cls).setUpClass()
        cls.property = ConfigurationProperty(
            "storage",
            namespace="name",
            private=["_test3"],
            defaults=MOCK_CONFIGURATION
        )

    def test_getter(self):
        self.assertFalse(hasattr(self, "storage"))
        self.assertIsInstance(self.property, ConfigurationType)
        self.assertTrue(hasattr(self, "storage"))

    def test_setter(self):
        self.assertFalse(hasattr(self, "storage"))
        self.property = {}
        self.assertIsInstance(self.property, ConfigurationType)
        self.assertTrue(hasattr(self, "storage"))

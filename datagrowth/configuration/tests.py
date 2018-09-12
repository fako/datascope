from django.test import TestCase

from datagrowth.configuration import (ConfigurationType, ConfigurationNotFoundError, ConfigurationProperty, load_config,
                                      MOCK_CONFIGURATION)


class TestConfigurationType(TestCase):

    def setUp(self):
        self.config = ConfigurationType(namespace="name", private=["_test3"], defaults=MOCK_CONFIGURATION)
        self.config.update({
            "test": "public",
            "_test2": "protected",
            "_test3": "private",
            "$test4": "variable"  # variable config is not recommended
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
        self.assertEqual(self.config._test2, "protected")
        self.assertEqual(self.config._test3, "private")
        self.assertEqual(self.config.test4, "variable")
        # Not found error
        try:
            self.test = self.config.test5
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

    def test_update_using_update(self):
        # Test (partial) updating
        self.config.update({"test": "public 2"})
        self.assertEqual(self.config.test, "public 2")
        self.assertEqual(self.config.test2, "protected")
        self.assertEqual(self.config.test3, "private")
        self.config.update({"_test2": "protected 2", "_test3": "private 2", "$test4": "variable 2"})
        self.assertEqual(self.config.test, "public 2")
        self.assertEqual(self.config.test2, "protected 2")
        self.assertEqual(self.config.test3, "private 2")
        self.assertEqual(self.config.test4, "variable 2")
        # Test private configuration detection
        self.config._private.append("_private_also")
        self.config.update({"private_also": "private"})
        self.assertEqual(self.config.private_also, "private")
        self.assertEqual(self.config._private_also, "private")

    def test_to_dict(self):
        # Get all different possibilities
        private = self.config.to_dict(private=True)
        protected = self.config.to_dict(protected=True)
        public = self.config.to_dict()
        everything = self.config.to_dict(private=True, protected=True)
        # Check properties
        self.assertIn("_test3", private)
        self.assertIn("test", private)
        self.assertIn("$test4", private)
        self.assertNotIn("_test2", private)
        self.assertIn("_test2", protected)
        self.assertIn("test", protected)
        self.assertIn("$test4", protected)
        self.assertNotIn("_test3", protected)
        self.assertIn("test", public)
        self.assertIn("$test4", public)
        self.assertNotIn("_test2", public)
        self.assertNotIn("_test3", public)
        self.assertIn("test", everything)
        self.assertIn("_test2", everything)
        self.assertIn("_test3", everything)
        self.assertIn("$test4", everything)
        # Make sure that all private keys are there
        # But the defaults key should not be passed down
        self.assertEqual(len(self.config._private) - 1 + len(public), len(private))

    def test_from_dict(self):
        # Call with correct dict
        type_instance = ConfigurationType.from_dict(
            self.config.to_dict(private=True, protected=True),
            MOCK_CONFIGURATION
        )
        self.assertEqual(type_instance.test, "public")
        self.assertEqual(type_instance.test2, "protected")
        self.assertEqual(type_instance.test3, "private")
        self.assertEqual(type_instance.test4, "variable")
        self.assertEqual(type_instance.global_configuration, "global configuration")
        self.assertEqual(type_instance.namespace_configuration, "namespace configuration")
        self.assertEqual(type_instance._private, self.config._private)
        # Call with malformed dicts
        try:
            ConfigurationType.from_dict({"_namespace": "test"}, MOCK_CONFIGURATION)
            self.fail("from_dict does not fail if _private is missing from configuration.")
        except AssertionError:
            pass
        try:
            ConfigurationType.from_dict({"_private": "test"}, MOCK_CONFIGURATION)
            self.fail("from_dict does not fail if _namespace is missing from configuration.")
        except AssertionError:
            pass

    def test_contains(self):
        self.skipTest("not tested")

    def test_supplement(self):
        self.skipTest("not tested")

    def test_items(self):
        self.skipTest("not tested")

    def test_clean_key(self):
        self.skipTest("not tested")

    def test_get(self):
        self.skipTest("not tested")


class ConfigurationPropertyHolder(object):
    property = ConfigurationProperty(
        "storage",
        namespace="name",
        private=["_test3"],
        defaults=MOCK_CONFIGURATION
    )


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

    def setUp(self):
        super(TestConfigurationProperty, self).setUp()
        self.holder1 = ConfigurationPropertyHolder()
        self.holder2 = ConfigurationPropertyHolder()

    def test_getter(self):
        self.assertFalse(hasattr(self, "storage"))
        self.assertIsInstance(self.property, ConfigurationType)
        self.assertTrue(hasattr(self, "storage"))

    def test_setter(self):
        self.assertFalse(hasattr(self, "storage"))
        self.property = {}
        self.assertIsInstance(self.property, ConfigurationType)
        self.assertTrue(hasattr(self, "storage"))

    def test_doubles(self):
        self.holder1.property = {"test": "test"}
        self.assertNotEqual(self.holder1.property, self.holder2.property)  # instances should not share configurations

    def test_set_with_type(self):
        self.holder1.property = {"test": "test"}
        self.holder2.property = self.holder1.property
        self.assertEqual(self.holder2.property.test, "test")
        self.assertNotEqual(self.holder1.property, self.holder2.property)  # instances should not share configurations


class TestLoadConfigDecorator(TestCase):

    def setUp(self):
        self.config = ConfigurationType(namespace="name", private=["_test3"], defaults=MOCK_CONFIGURATION)
        self.config.update({
            "test": "public",
            "_test2": "protected",
            "_test3": "private"
        })

    @staticmethod
    @load_config(defaults=MOCK_CONFIGURATION)
    def decorated(config, *args, **kwargs):
        return config, args, kwargs

    def test_decorator(self):
        # Standard call
        test_config, test_args, test_kwargs = self.decorated(
            "test",
            test="test",
            config=self.config.to_dict(protected=True, private=True)
        )
        self.assertIsInstance(test_config, ConfigurationType)
        self.assertEqual(test_config._defaults, MOCK_CONFIGURATION)
        self.assertEqual(test_config._namespace, "name")
        self.assertIn("_test3", test_config._private)
        self.assertEqual(self.config.test, "public")
        self.assertEqual(self.config.test2, "protected")
        self.assertEqual(self.config.test3, "private")
        self.assertEqual(self.config._test2, "protected")
        self.assertEqual(self.config._test3, "private")
        self.assertEqual(test_args, ("test",))
        self.assertEqual(test_kwargs, {"test": "test"})
        # Call with config set to a ConfigurationType
        test_config, test_args, test_kwargs = self.decorated(
            "test",
            test="test",
            config=self.config
        )
        self.assertEqual(test_config, self.config)
        self.assertEqual(test_args, ("test",))
        self.assertEqual(test_kwargs, {"test": "test"})
        # Wrong invocation
        try:
            test_config, test_args, test_kwargs = self.decorated(
                "test",
                test="test",
            )
            self.fail("load_config did not throw an exception when no config kwarg was set.")
        except TypeError:
            pass


class TestGetStandardizedConfiguration(TestCase):

    def test_standardized_configuration(self):
        self.skipTest("not tested")

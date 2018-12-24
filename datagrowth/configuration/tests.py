from mock import patch
from collections import Iterator

from django.test import TestCase

from datagrowth.configuration import (ConfigurationType, ConfigurationNotFoundError, ConfigurationProperty, load_config,
                                      get_standardized_configuration, MOCK_CONFIGURATION, DEFAULT_CONFIGURATION,
                                      create_config, register_defaults)


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
        # Implicit init without defaults
        # Notice that apps can manipulate the DEFAULT_CONFIGURATION upon app.ready
        # Therefor defaults are not loaded until first access
        instance = ConfigurationType()
        self.assertEqual(instance._defaults, None)
        self.assertEqual(instance._namespace, ConfigurationType._global_prefix)
        self.assertEqual(instance._private, ConfigurationType._private_defaults)
        purge_immediately = instance.purge_immediately  # this loads the defaults
        self.assertFalse(purge_immediately)
        self.assertEqual(instance._defaults, DEFAULT_CONFIGURATION)
        # Implicit init with defaults
        instance = ConfigurationType(defaults=MOCK_CONFIGURATION)
        self.assertEqual(instance._defaults, MOCK_CONFIGURATION)
        self.assertEqual(instance._namespace, ConfigurationType._global_prefix)
        self.assertEqual(instance._private, ConfigurationType._private_defaults)
        purge_immediately = instance.purge_immediately  # this won't load defaults as defaults got set
        self.assertFalse(purge_immediately)
        self.assertEqual(instance._defaults, MOCK_CONFIGURATION)
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
        self.assertTrue("test" in self.config)
        self.assertTrue("test2" in self.config)
        self.assertTrue("test3" in self.config)
        self.assertTrue("_test2" in self.config)
        self.assertTrue("_test3" in self.config)
        self.assertTrue("test4" in self.config)
        self.assertFalse("test5" in self.config)

    @patch("datagrowth.configuration.types.ConfigurationType.update")
    def test_supplement(self, update_method):
        self.config.supplement({"test": "public 2"})
        self.assertEqual(self.config.test, "public")
        update_method.assert_not_called()
        self.config.supplement({"_test2": "protected 2", "_test3": "private 2", "$test4": "variable 2"})
        self.assertEqual(self.config.test, "public")
        self.assertEqual(self.config.test2, "protected")
        self.assertEqual(self.config.test3, "private")
        self.assertEqual(self.config.test4, "variable")
        update_method.assert_not_called()
        self.config.supplement({"new": "new", "_new2": "new 2", "$new3": "new 3"})
        update_method.assert_called_once_with({"new": "new", "_new2": "new 2", "$new3": "new 3"})

    def test_items(self):
        # Get all different possibilities
        private = self.config.items(private=True)
        protected = self.config.items(protected=True)
        public = self.config.items()
        everything = self.config.items(private=True, protected=True)
        # Check types
        self.assertIsInstance(private, Iterator)
        self.assertIsInstance(protected, Iterator)
        self.assertIsInstance(public, Iterator)
        self.assertIsInstance(everything, Iterator)
        # Convert to more predictable dicts
        private = dict(private)
        protected = dict(protected)
        public = dict(public)
        everything = dict(everything)
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

    def test_clean_key(self):
        variable_key = "$variable"
        protected_key = "_protected"
        weird_key = ",weird"
        self.assertEqual(self.config.clean_key(variable_key), "variable")
        self.assertEqual(self.config.clean_key(protected_key), "protected")
        self.assertEqual(self.config.clean_key(weird_key), ",weird")

    def test_get(self):
        self.assertEqual(self.config.get("test", None), "public")
        self.assertEqual(self.config.get("test2", None), "protected")
        self.assertEqual(self.config.get("test3", None), "private")
        self.assertEqual(self.config.get("_test2", None), "protected")
        self.assertEqual(self.config.get("_test3", None), "private")
        self.assertEqual(self.config.get("test4", None), "variable")
        # Default fallback
        self.assertEqual(self.config.get("test5", "does-not-exist"), "does-not-exist")
        # Namespace configuration (with a list default)
        self.assertNotIn("namespace_configuration", self.config.__dict__)
        self.assertEqual(self.config.get("namespace_configuration", None), "namespace configuration")
        self.assertEqual(self.config.get("namespace_missing", ["missing namespace"]), ["missing namespace"])
        # Global configuration (with a dict default)
        self.assertNotIn("global_configuration", self.config.__dict__)
        self.assertEqual(self.config.get("global_configuration", None), "global configuration")
        self.assertEqual(self.config.get("global_missing", {"global missing": True}), {"global missing": True})
        try:
            self.test = self.config.get("test5")
            self.fail(
                "ConfigurationType.get should raise an exception "
                "when configuration is not available and no default is set"
            )
        except ConfigurationNotFoundError:
            pass


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

    def setUp(self):
        self.config = ConfigurationType(namespace="name", private=["_test3"], defaults=MOCK_CONFIGURATION)
        self.config.update({
            "test": "public",
            "_test2": "protected",
            "_test3": "private"
        })

    def test_standardized_configuration(self):
        out = get_standardized_configuration(self.config)
        self.assertEqual(out, "3601ce2b866f9ccff5e9e49b628e65108abb3d5ada72fce6511645212c0ce520")
        out = get_standardized_configuration(self.config, as_hash=False)
        self.assertEqual(out, "test=public")


class TestCreateConfig(TestCase):

    def test_create_config(self):
        test_config = create_config("name", {
            "test": "public",
            "_test2": "protected",
            "_test3": "protected 2"
        })
        self.assertIsNone(test_config._defaults)
        self.assertIsInstance(test_config, ConfigurationType)
        self.assertEqual(test_config.test, "public")
        self.assertEqual(test_config.test2, "protected")
        self.assertEqual(test_config.test3, "protected 2")
        self.assertEqual(test_config._test2, "protected")
        self.assertEqual(test_config._test3, "protected 2")

    def test_create_config_registered_defaults(self):
        register_defaults("name", {
            "test4": "namespaced default"
        })
        test_config = create_config("name", {
            "test": "public",
            "_test2": "protected",
            "_test3": "protected 2"
        })
        self.assertIsNone(test_config._defaults)
        self.assertIsInstance(test_config, ConfigurationType)
        self.assertEqual(test_config._namespace, "name")
        self.assertEqual(test_config.test4, "namespaced default")
        self.assertEqual(test_config._defaults, DEFAULT_CONFIGURATION)


class TestRegisterConfigDefaults(TestCase):

    def test_register_config_defaults(self):
        self.assertFalse(DEFAULT_CONFIGURATION["global_purge_immediately"])
        register_defaults("global", {
            "purge_immediately": True
        })
        self.assertTrue(DEFAULT_CONFIGURATION["global_purge_immediately"])
        self.assertNotIn("mock_test", DEFAULT_CONFIGURATION)
        register_defaults("mock", {
            "test": "create"
        })
        self.assertEqual(DEFAULT_CONFIGURATION["mock_test"], "create")

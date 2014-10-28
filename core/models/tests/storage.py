from django.test import TestCase

from mock import Mock

from core.models.storage import Storage, TextStorage
from core.helpers.configuration import Config
from core.helpers.storage import Container
from core.exceptions import HIFCouldNotLoadFromStorage


class TestStorage(TestCase):
    fixtures = ['test-storage']

    @classmethod
    def setUpClass(cls):
        cls.test_args = [u'test']
        cls.test_config = {'test': u'test'}
        ###cls.test_subs = {'TextStorage': [1, 2, 3]}

    def test_storage_init(self):
        """
        setup() will fail if initial values are not None
        """
        instance = Storage()
        self.assertEqual(instance.config, None)
        self.assertEqual(instance.arguments, None)
        ###self.assertEqual(instance.subs, None)

    def test_identifier(self):
        instance = TextStorage()
        identity = instance.identifier()
        self.assertEqual(identity, "0")
        instance.id = 1
        identity = instance.identifier()
        self.assertEqual(identity, "1")
        instance.args = []
        instance.config = Config(namespace='TEST',private=[])
        identity = instance.identifier()
        self.assertEqual(identity, "[] | {}")

    def test_serialize(self):
        """
        Serialized values should consist of the form ('ModelName', 1,)
        Save should be called upon serialization
        """
        instance = TextStorage()
        instance.save()
        instance.save = Mock(return_value=True)
        serialization = instance.serialize()
        self.assertIsInstance(serialization, tuple)
        self.assertEqual(len(serialization), 2)
        self.assertEqual(serialization[0], instance.type)
        self.assertEqual(serialization[1], instance.id)
        self.assertTrue(instance.save.called)

    def test_load_without_serialization(self):
        # Load fail
        instance = TextStorage()
        instance.body = "Unloaded"
        try:
            instance.load()
            self.fail()
        except HIFCouldNotLoadFromStorage as exception:
            self.assertEqual(str(exception), "{} with identifier={} and type={} does not exist".format(instance.__class__, instance.identity, instance.type))
        self.assertEqual(instance.body, "Unloaded")
        # Load success
        instance.identity = "[u'test'] | {'test': u'test'}"
        instance.type = "TextStorage"
        instance.load()
        self.assertEqual(instance.body, "Test text 1")

    def test_load_with_serialization(self):
        # Load fail wrong id
        instance = TextStorage()
        instance.body = "Unloaded"
        try:
            instance.load(("TextStorage", 1000000,))
            self.fail()
        except HIFCouldNotLoadFromStorage as exception:
            self.assertEqual(str(exception), "{} with id=1000000 does not exist".format(instance.__class__))
        self.assertEqual(instance.body, "Unloaded")
        # Load success
        instance.load(("TextStorage", 1,))
        self.assertEqual(instance.body, "Test text 1")

    def test_setup(self):
        args = self.test_args
        config = self.test_config
        ###subs = self.test_subs
        filled_instance = TextStorage(arguments=args, configuration=config) ###, substorage=subs)
        filled_instance.identity = "0"
        # Setup does nothing when arguments and/or config are set
        # It doesn't try to load instances from the db if identity is set, leaving body field empty
        # It should however setup substorage properly
        ignored_args = ['ignored']
        ignored_config = {'ignored':'ignored'}
        filled_instance.setup(*ignored_args, **ignored_config)
        self.assertIsInstance(filled_instance.args, list)
        self.assertEqual(filled_instance.arguments, args)
        self.assertEqual(filled_instance.args, args)
        self.assertIsInstance(filled_instance.config, Config)
        self.assertEqual(filled_instance.configuration, config)
        self.assertEqual(filled_instance.config.dict(), config)
        self.assertEqual(filled_instance.config.test, "test")
        ### self.assertIsInstance(filled_instance.subs, Container)
        ### self.assertEqual(filled_instance.substorage, subs)
        ### self.assertEqual(filled_instance.subs.dict(), subs)
        self.assertEqual(filled_instance.identity, "0")
        self.assertEqual(filled_instance.body, "")
        # Setup sets vars if instance is empty
        # It should also call load and set body field since identity is not set
        # Substorage can't be passed to setup and setup should make it an empty container
        s_args = ['test']  # using strings to test unicode transformations
        s_config = {'test': 'test'}
        empty_instance = TextStorage()
        empty_instance.setup(*s_args, **s_config)
        self.assertIsInstance(empty_instance.args, list)
        self.assertEqual(empty_instance.arguments, args)
        self.assertEqual(empty_instance.args, args)
        self.assertIsInstance(empty_instance.config, Config)
        self.assertEqual(empty_instance.configuration, config)
        self.assertEqual(empty_instance.config.dict(), config)
        self.assertEqual(empty_instance.config.test, "test")
        #self.assertIsInstance(empty_instance.subs, Container)
        #self.assertEqual(empty_instance.substorage, None)
        #self.assertEqual(empty_instance.subs.dict(), {})
        self.assertEqual(empty_instance.identity, "{} | {}".format(args, config))
        self.assertEqual(empty_instance.body, "Test text 1")

    def test_retain(self):
        instance = TextStorage()
        instance.serialize = Mock(return_value=True)
        instance.setup()
        # No args, config or subs given
        instance.retain()
        self.assertEqual(instance.arguments, None)
        self.assertEqual(instance.configuration, None)
        ### self.assertEqual(instance.substorage, None)
        self.assertEqual(instance.retained, True)
        self.assertTrue(instance.serialize.called)
        # Args, config and subs given
        instance.args = self.test_args
        instance.config(self.test_config)
        ###instance.subs(self.test_subs)
        instance.serialize = Mock(return_value=True)
        instance.retain()
        self.assertEqual(instance.arguments, self.test_args)
        self.assertDictContainsSubset(self.test_config, instance.configuration)
        ###self.assertEqual(instance.substorage, self.test_subs)
        self.assertEqual(instance.retained, True)
        self.assertTrue(instance.serialize.called)
        # Retain without serialization
        instance = TextStorage()
        instance.serialize = Mock(return_value=True)
        instance.setup()
        instance.retain(serialize=False)
        self.assertFalse(instance.serialize.called)

    def test_release(self):
        instance = TextStorage(retained=True)
        instance.save = Mock(return_value=True)
        instance.release()
        self.assertFalse(instance.retained)
        self.assertTrue(instance.save.called)
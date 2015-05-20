from django.test import TestCase
from django.utils import six

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType


class TestFetch(TestCase):

    fixtures = ["test-http-resource-mock"]

    def setUp(self):
        super(TestFetch, self).setUp()
        self.config = ConfigurationType(
            namespace="http_resource",
            private=["_resource", "_continuation_limit"],
            defaults=MOCK_CONFIGURATION
        )
        self.config.set_configuration({
            "resource": "HttpResourceMock",
        })

    def check_results(self, results, expected_length):
        self.assertEqual(len(results), expected_length)
        for id in results:
            self.assertIsInstance(id, six.integer_types)
            self.assertGreater(id, 0)

    def test_single_fetch(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        rsl, err = HttpResourceProcessor._fetch("test", config=self.config)
        self.check_results(rsl, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        rsl, err = HttpResourceProcessor._fetch("success", config=self.config,)
        self.check_results(rsl, 1)
        self.check_results(err, 0)
        # And with an error response
        rsl, err = HttpResourceProcessor._fetch("404", config=self.config)
        self.check_results(rsl, 0)
        self.check_results(err, 1)
        rsl, err = HttpResourceProcessor._fetch("500", config=self.config)
        self.check_results(rsl, 0)
        self.check_results(err, 1)

    def test_continuation_prohibited_fetch(self):
        pass

    def test_continuation_fetch(self):
        pass

    def test_inserted_session_fetch(self):
        pass
from datetime import datetime

from django.test import TestCase
from django.utils import six

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType
from core.tests.mocks import MockRequestsWithAgent, MockRequests
from sources.models.local import HttpResourceMock


class TestSend(TestCase):

    fixtures = ["test-http-resource-mock"]

    def setUp(self):
        super(TestSend, self).setUp()
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

    def test_send(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        scc, err = HttpResourceProcessor._send("get", "test", config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        scc, err = HttpResourceProcessor._send("get", "success", config=self.config,)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # And with an error response
        scc, err = HttpResourceProcessor._send("get", "404", config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)
        scc, err = HttpResourceProcessor._send("get", "500", config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)

    def test_send_continuation_prohibited(self):
        scc, err = HttpResourceProcessor._send("get", "next", config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)

    def test_send_continuation(self):
        self.config.continuation_limit = 10
        scc, err = HttpResourceProcessor._send("get", "next", config=self.config)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_inserted_session(self):
        scc, err = HttpResourceProcessor._send("get", "test", config=self.config, session=MockRequestsWithAgent)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        link = HttpResourceMock.objects.get(id=scc[0])
        self.assertIn("User-Agent", link.head)

    def test_send_mass(self):
        args_list = [["test"], ["test2"], ["404"]]
        kwargs_list = [{}, {}, {}]
        start = datetime.now()
        scc, err = HttpResourceProcessor._send_mass("get", args_list, kwargs_list, config=self.config, session=MockRequests)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.assertLess(duration, 0.01)
        self.check_results(scc, 2)
        self.check_results(err, 1)

    def test_send_mass_intervals(self):
        self.config.interval_duration = 250  # 0.25 secs
        args_list = [["test"], ["test2"]]
        kwargs_list = [{}, {}]
        start = datetime.now()
        scc, err = HttpResourceProcessor._send_mass("get", args_list, kwargs_list, config=self.config, session=MockRequests)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.assertGreater(duration, 0.5)
        self.assertLess(duration, 1)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_mass_continuation_prohibited(self):
        args_list = [["test"], ["next"], ["404"]]
        kwargs_list = [{}, {}, {}]
        scc, err = HttpResourceProcessor._send_mass("get", args_list, kwargs_list, config=self.config, session=MockRequests)
        self.check_results(scc, 2)
        self.check_results(err, 1)

    def test_send_mass_continuation(self):
        self.config.continuation_limit = 10
        args_list = [["test"], ["next"], ["404"]]
        kwargs_list = [{}, {}, {}]
        scc, err = HttpResourceProcessor._send_mass("get", args_list, kwargs_list, config=self.config, session=MockRequests)
        self.check_results(scc, 3)
        self.check_results(err, 1)

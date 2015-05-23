from datetime import datetime

from django.test import TestCase
from django.utils import six

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType
from core.tests.mocks import MockRequestsWithAgent, MockRequests
from sources.models.local import HttpResourceMock


class TestHttpResourceProcessorMixin(TestCase):

    fixtures = ["test-http-resource-mock"]

    def setUp(self):
        super(TestHttpResourceProcessorMixin, self).setUp()
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


class TestHttpResourceProcessor(TestHttpResourceProcessorMixin, TestCase):

    def test_get_link(self):
        self.fail("test")

    def test_fetch(self):
        self.fail("test")

    def test_fetch_mass(self):
        self.fail("test")

    def test_submit(self):
        self.fail("test")

    def test_submit_mass(self):
        self.fail("test")


class TestHttpResourceProcessorBase(TestHttpResourceProcessorMixin, TestCase):

    method = ""

    def get_args_list(self, queries):
        if self.method == "get":
            return [[query] for query in queries]
        elif self.method == "post":
            return [[] for query in queries]
        else:
            raise Exception("{} does not have a valid method specified.".format(self.__class__.__name__))

    def get_kwargs_list(self, queries):
        if self.method == "get":
            return [{} for query in queries]
        elif self.method == "post":
            return [{"query": query} for query in queries]
        else:
            raise Exception("{} does not have a valid method specified.".format(self.__class__.__name__))


    def test_send_mass(self):
        args_list = self.get_args_list(["test", "test2", "404"])
        kwargs_list = self.get_kwargs_list(["test", "test2", "404"])
        start = datetime.now()
        scc, err = HttpResourceProcessor._send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.assertLess(duration, 0.01)
        self.check_results(scc, 2)
        self.check_results(err, 1)

    def test_send_mass_intervals(self):
        self.config.interval_duration = 250  # 0.25 secs
        args_list = self.get_args_list(["test", "test2"])
        kwargs_list = self.get_kwargs_list(["test", "test2"])
        start = datetime.now()
        scc, err = HttpResourceProcessor._send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.assertGreater(duration, 0.5)
        self.assertLess(duration, 1)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_mass_continuation_prohibited(self):
        args_list = self.get_args_list(["test", "next", "404"])
        kwargs_list = self.get_kwargs_list(["test", "next", "404"])
        scc, err = HttpResourceProcessor._send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        self.check_results(scc, 2)
        self.check_results(err, 1)

    def test_send_mass_continuation(self):
        self.config.continuation_limit = 10
        args_list = self.get_args_list(["test", "next", "404"])
        kwargs_list = self.get_kwargs_list(["test", "next", "404"])
        scc, err = HttpResourceProcessor._send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        self.check_results(scc, 3)
        self.check_results(err, 1)


class TestHttpResourceProcessorGet(TestHttpResourceProcessorBase):

    method = "get"

    def test_send(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        scc, err = HttpResourceProcessor._send("test", method=self.method, config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        scc, err = HttpResourceProcessor._send("success", method=self.method, config=self.config,)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # And with an error response
        scc, err = HttpResourceProcessor._send("404", method=self.method, config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)
        scc, err = HttpResourceProcessor._send("500", method=self.method, config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)

    def test_send_continuation_prohibited(self):
        scc, err = HttpResourceProcessor._send("next", method=self.method, config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)

    def test_send_continuation(self):
        self.config.continuation_limit = 10
        scc, err = HttpResourceProcessor._send("next", method=self.method, config=self.config)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_inserted_session(self):
        scc, err = HttpResourceProcessor._send("test", method=self.method, config=self.config, session=MockRequestsWithAgent)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        link = HttpResourceMock.objects.get(id=scc[0])
        self.assertIn("User-Agent", link.head)


class TestHttpResourceProcessorPost(TestHttpResourceProcessorBase):

    method = "post"

    def test_send(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        scc, err = HttpResourceProcessor._send(query="test", method=self.method, config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        scc, err = HttpResourceProcessor._send(query="success", method=self.method, config=self.config,)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # And with an error response
        scc, err = HttpResourceProcessor._send(query="404", method=self.method, config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)
        scc, err = HttpResourceProcessor._send(query="500", method=self.method, config=self.config)
        self.check_results(scc, 0)
        self.check_results(err, 1)

    def test_send_continuation_prohibited(self):
        scc, err = HttpResourceProcessor._send(query="next", method=self.method, config=self.config)
        self.check_results(scc, 1)
        self.check_results(err, 0)

    def test_send_continuation(self):
        self.config.continuation_limit = 10
        scc, err = HttpResourceProcessor._send(query="next", method=self.method, config=self.config)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_inserted_session(self):
        scc, err = HttpResourceProcessor._send(query="test", method=self.method, config=self.config, session=MockRequestsWithAgent)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        link = HttpResourceMock.objects.get(id=scc[0])
        self.assertIn("User-Agent", link.head)



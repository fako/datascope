from datetime import datetime

import requests
from mock import patch

from django.test import TestCase
from django.utils import six

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType
from core.tests.mocks.requests import MockRequestsWithAgent, MockRequests
from core.tests.mocks.celery import MockTask
from core.tests.mocks.http import HttpResourceMock


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
        for pk in results:
            self.assertIsInstance(pk, six.integer_types)
            self.assertGreater(pk, 0)


class TestHttpResourceProcessor(TestHttpResourceProcessorMixin, TestCase):

    def setUp(self):
        super(TestHttpResourceProcessor, self).setUp()
        self.prc = HttpResourceProcessor(config=self.config.to_dict(protected=True, private=True))
        self.prc._send = MockTask
        self.prc._send_mass = MockTask
        MockTask.reset_mock()

    def test_get_link(self):
        self.config.set_configuration({"test": "test"})
        session = requests.Session()
        session.cookies = {"test": "test"}
        link = HttpResourceProcessor.get_link(config=self.config, session=session)
        self.assertIsInstance(link, HttpResourceMock)
        self.assertIsNone(link.id)
        self.assertIsNone(link.request)
        self.assertFalse(hasattr(link.config, 'resource'))
        self.assertEqual(link.config.test, 'test')
        self.assertEqual(link.session.cookies, {"test": "test"})

    def test_fetch(self):
        null = self.prc.fetch
        self.assertTrue(self.prc._send.s.called)
        args, kwargs = self.prc._send.s.call_args
        self.assertEqual(kwargs["method"], "get")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    def test_fetch_mass(self):
        null = self.prc.fetch_mass
        self.assertTrue(self.prc._send_mass.s.called)
        args, kwargs = self.prc._send_mass.s.call_args
        self.assertEqual(kwargs["method"], "get")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    def test_submit(self):
        null = self.prc.submit
        self.assertTrue(self.prc._send.s.called)
        args, kwargs = self.prc._send.s.call_args
        self.assertEqual(kwargs["method"], "post")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    def test_submit_mass(self):
        null = self.prc.submit_mass
        self.assertTrue(self.prc._send_mass.s.called)
        args, kwargs = self.prc._send_mass.s.call_args
        self.assertEqual(kwargs["method"], "post")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))


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
        self.assertLess(duration, 0.1)
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
        scc, err = HttpResourceProcessor._send_mass(
            args_list,
            kwargs_list,
            method=self.method,
            config=self.config,
            session=MockRequests
        )
        self.check_results(scc, 3)
        self.check_results(err, 1)

    @patch("core.processors.resources.HttpResourceProcessor._send_serie", return_value=([], [],))
    def test_send_mass_concat_arguments(self, send_serie):
        self.config.concat_args_size = 3
        self.config.concat_args_symbol = "|"
        scc, err = HttpResourceProcessor._send_mass(
            [[1], [2], [3], [4], [5, 5], [6], [7]],
            [{}, {}, {}, {}, {}, {}, {}],
            method=self.method,
            config=self.config,
            session=MockRequests
        )
        send_serie.assert_called_with([["1|2|3"], ["4|5|5|6"], ["7"]], [{}, {}, {}], method=self.method, config=self.config, session=MockRequests)

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

    def test_async_results(self):
        self.skipTest("not tested")

    def test_results(self):
        self.skipTest("not tested")

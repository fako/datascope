from datetime import datetime

from mock import patch
import requests

from django.test import TestCase
from django.utils import six

from datascope.configuration import MOCK_CONFIGURATION
from core.tasks.http import send, send_serie, send_mass, get_resource_link, load_session
from core.utils.configuration import ConfigurationType
from core.tests.mocks.requests import MockRequestsWithAgent, MockRequests
from core.tests.mocks.http import HttpResourceMock


class TestHTTPTasksBase(TestCase):

    fixtures = ["test-http-resource-mock"]
    method = ""

    def setUp(self):
        super(TestHTTPTasksBase, self).setUp()
        self.config = ConfigurationType(
            namespace="http_resource",
            private=["_resource", "_continuation_limit"],
            defaults=MOCK_CONFIGURATION
        )
        self.config.set_configuration({
            "resource": "HttpResourceMock",
        })
        self.session = MockRequests

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

    def check_results(self, results, expected_length):
        self.assertEqual(len(results), expected_length)
        for pk in results:
            self.assertIsInstance(pk, six.integer_types)
            self.assertGreater(pk, 0)


class TestSendMassTaskBase(TestHTTPTasksBase):

    def test_send_mass(self):
        args_list = self.get_args_list(["test", "test2", "404"])
        kwargs_list = self.get_kwargs_list(["test", "test2", "404"])
        start = datetime.now()
        scc, err = send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
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
        scc, err = send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        end = datetime.now()
        duration = (end - start).total_seconds()
        self.assertGreater(duration, 0.5)
        self.assertLess(duration, 1)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_mass_continuation_prohibited(self):
        args_list = self.get_args_list(["test", "next", "404"])
        kwargs_list = self.get_kwargs_list(["test", "next", "404"])
        scc, err = send_mass(args_list, kwargs_list, method=self.method, config=self.config, session=MockRequests)
        self.check_results(scc, 2)
        self.check_results(err, 1)

    def test_send_mass_continuation(self):
        self.config.continuation_limit = 10
        args_list = self.get_args_list(["test", "next", "404"])
        kwargs_list = self.get_kwargs_list(["test", "next", "404"])
        scc, err = send_mass(
            args_list,
            kwargs_list,
            method=self.method,
            config=self.config,
            session=MockRequests
        )
        self.check_results(scc, 3)
        self.check_results(err, 1)

    @patch("core.tasks.http.send_serie", return_value=([], [],))
    def test_send_mass_concat_arguments(self, send_serie):
        self.config.concat_args_size = 3
        self.config.concat_args_symbol = "|"
        scc, err = send_mass(
            [[1], [2], [3], [4], [5, 5], [6], [7]],
            [{}, {}, {}, {}, {}, {}, {}],
            method=self.method,
            config=self.config,
            session=MockRequests
        )
        send_serie.assert_called_with(
            [["1|2|3"], ["4|5|5|6"], ["7"]], [{}, {}, {}],
            method=self.method,
            config=self.config,
            session=MockRequests
        )

    def test_send_inserted_session_provider(self):
        self.skipTest("not tested")


class TestSendMassTaskGet(TestSendMassTaskBase):
    method = "get"


class TestSendMassTaskPost(TestSendMassTaskBase):
    method = "post"


class TestSendTaskGet(TestHTTPTasksBase):

    method = "get"

    def test_send(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        scc, err = send("test", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        scc, err = send("success", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # And with an error response
        scc, err = send("404", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 0)
        self.check_results(err, 1)
        scc, err = send("500", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 0)
        self.check_results(err, 1)

    def test_send_continuation_prohibited(self):
        scc, err = send("next", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)

    def test_send_continuation(self):
        self.config.continuation_limit = 10
        scc, err = send("next", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_inserted_session(self):
        scc, err = send("test", method=self.method, config=self.config, session=MockRequestsWithAgent)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        link = HttpResourceMock.objects.get(id=scc[0])
        self.assertIn("user-agent", link.head)

    def test_send_inserted_session_provider(self):
        self.skipTest("not tested")


class TestSendTaskPost(TestHTTPTasksBase):

    method = "post"

    def test_send(self):
        # Test makes equivalent call of HttpResourceProcessor.fetch.delay("test")
        scc, err = send(query="test", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # Similar but with a cached result
        scc, err = send(query="success", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        # And with an error response
        scc, err = send(query="404", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 0)
        self.check_results(err, 1)
        scc, err = send(query="500", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 0)
        self.check_results(err, 1)

    def test_send_continuation_prohibited(self):
        scc, err = send(query="next", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 1)
        self.check_results(err, 0)

    def test_send_continuation(self):
        self.config.continuation_limit = 10
        scc, err = send(query="next", method=self.method, config=self.config, session=self.session)
        self.check_results(scc, 2)
        self.check_results(err, 0)

    def test_send_inserted_session(self):
        scc, err = send(query="test", method=self.method, config=self.config, session=MockRequestsWithAgent)
        self.check_results(scc, 1)
        self.check_results(err, 0)
        link = HttpResourceMock.objects.get(id=scc[0])
        self.assertIn("user-agent", link.head)

    def test_send_inserted_session_provider(self):
        self.skipTest("not tested")


class TestSendSerieTaskGet(TestHTTPTasksBase):

    def test_case(self):
        # TODO: very similar to TestSendMassTaskGet, refactor?
        self.skipTest("not tested")


    def test_send_inserted_session_provider(self):
        self.skipTest("not tested")


class TestSendSerieTaskPost(TestHTTPTasksBase):

    def test_case(self):
        # TODO: very similar to TestSendMassTaskPost, refactor?
        self.skipTest("not tested")

    def test_send_inserted_session_provider(self):
        self.skipTest("not tested")


class TestGetResourceLink(TestHTTPTasksBase):

    def test_get_link(self):
        self.config.set_configuration({"test": "test"})
        session = requests.Session()
        session.cookies = {"test": "test"}
        link = get_resource_link(config=self.config, session=session)
        self.assertIsInstance(link, HttpResourceMock)
        self.assertIsNone(link.id)
        self.assertIsNone(link.request)
        self.assertFalse(hasattr(link.config, 'resource'))
        self.assertEqual(link.config.test, 'test')
        self.assertEqual(link.session.cookies, {"test": "test"})


class TestLoadSession(TestCase):

    def test_load_session(self):
        self.skipTest("not tested")

    def test_preload_session(self):
        self.skipTest("not tested")

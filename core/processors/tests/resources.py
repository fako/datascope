from datetime import datetime

import requests
from mock import patch

from django.test import TestCase
from django.utils import six
from django.db.models import QuerySet

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType
from core.tests.mocks.requests import MockRequestsWithAgent, MockRequests
from core.tests.mocks.celery import (MockTask, MockAsyncResultSuccess, MockAsyncResultPartial, MockAsyncResultError,
                                     MockAsyncResultWaiting)
from core.tests.mocks.http import HttpResourceMock
from core.exceptions import DSProcessUnfinished, DSProcessError


class TestHttpResourceProcessor(TestCase):

    fixtures = ["test-http-resource-mock"]

    def setUp(self):
        super(TestHttpResourceProcessor, self).setUp()
        self.config = ConfigurationType(
            namespace="http_resource",
            private=["_resource", "_continuation_limit"],
            defaults=MOCK_CONFIGURATION
        )
        self.config.set_configuration({
            "resource": "HttpResourceMock",
        })
        self.prc = HttpResourceProcessor(config=self.config.to_dict(protected=True, private=True))
        self.prc._send = MockTask
        self.prc._send_mass = MockTask
        self.session = MockRequests
        MockTask.reset_mock()

    @patch("core.tasks.http.send.s")
    def test_fetch(self, send_s):
        null = self.prc.fetch
        self.assertTrue(send_s.called)
        args, kwargs = send_s.call_args
        self.assertEqual(kwargs["method"], "get")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    @patch("core.tasks.http.send_mass.s")
    def test_fetch_mass(self, send_mass_s):
        null = self.prc.fetch_mass
        self.assertTrue(send_mass_s.called)
        args, kwargs = send_mass_s.call_args
        self.assertEqual(kwargs["method"], "get")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    @patch("core.tasks.http.send.s")
    def test_submit(self, send_s):
        null = self.prc.submit
        self.assertTrue(send_s.called)
        args, kwargs = send_s.call_args
        self.assertEqual(kwargs["method"], "post")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    @patch("core.tasks.http.send_mass.s")
    def test_submit_mass(self, send_mass_s):
        null = self.prc.submit_mass
        self.assertTrue(send_mass_s.called)
        args, kwargs = send_mass_s.call_args
        self.assertEqual(kwargs["method"], "post")
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_resource"))

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_async_results_success(self, async_result):
        scc, err = self.prc.async_results("result-id")
        async_result.assert_called_once_with("result-id")
        self.assertEqual(scc, [1, 2, 3])
        self.assertEqual(err, [])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultPartial)
    def test_async_results_partial(self, async_result):
        scc, err = self.prc.async_results("result-id")
        async_result.assert_called_once_with("result-id")
        self.assertEqual(scc, [1, 2, 3])
        self.assertEqual(err, [4, 5])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultWaiting)
    def test_async_results_waiting(self, async_result):
        try:
            self.prc.async_results("result-id")
            self.fail("async_results did not raise when waiting for results")
        except DSProcessUnfinished:
            pass
        async_result.assert_called_once_with("result-id")

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultError)
    def test_async_results_error(self, async_result):
        try:
            self.prc.async_results("result-id")
            self.fail("async_results did not raise when waiting for results")
        except DSProcessError:
            pass
        async_result.assert_called_once_with("result-id")

    def test_results_success(self):
        scc, err = self.prc.results(([1, 2, 3], [],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(1, 4), scc.all()):
            self.assertIsInstance(result, HttpResourceMock)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 3)
        self.assertEqual(err.count(), 0)

    def test_results_partial(self):
        scc, err = self.prc.results(([1, 2, 3], [4, 5],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(1, 4), scc.all()):
            self.assertIsInstance(result, HttpResourceMock)
            self.assertEqual(result.id, index)
        for index, result in zip(range(4, 6), err.all()):
            self.assertIsInstance(result, HttpResourceMock)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 3)
        self.assertEqual(err.count(), 2)

    def test_results_error(self):
        scc, err = self.prc.results(([], [4, 5],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(4, 6), err.all()):
            self.assertIsInstance(result, HttpResourceMock)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 0)
        self.assertEqual(err.count(), 2)

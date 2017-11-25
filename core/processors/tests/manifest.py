from mock import patch
from types import GeneratorType

from django.test import TestCase
from django.db.models import QuerySet

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.manifest import ManifestProcessor
from core.utils.configuration import ConfigurationType
from core.tests.mocks.celery import (MockTask, MockAsyncResultSuccess, MockAsyncResultPartial, MockAsyncResultError,
                                     MockAsyncResultWaiting)
from core.models.resources.manifestation import Manifestation
from core.models import Individual
from core.exceptions import DSProcessUnfinished, DSProcessError


class TestManifestProcessor(TestCase):

    fixtures = ["test-manifestation", "test-organisms"]

    def setUp(self):
        super(TestManifestProcessor, self).setUp()
        self.config = ConfigurationType(
            namespace="manifest_processor",
            private=[],
            defaults=MOCK_CONFIGURATION
        )
        self.config.set_configuration({
            "_community": "CommunityMock",
        })
        self.prc = ManifestProcessor(config=self.config.to_dict(protected=True, private=True))
        MockTask.reset_mock()

    @patch("core.tasks.manifestation.manifest_serie.s")
    def test_manifest_mass(self, manifest_serie_s):
        null = self.prc.manifest_mass
        self.assertTrue(manifest_serie_s.called)
        args, kwargs = manifest_serie_s.call_args
        self.assertIsInstance(kwargs["config"], dict)
        self.assertTrue(kwargs["config"].get("_community"))

    @patch('core.processors.manifest.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_async_results_success(self, async_result):
        scc, err = self.prc.async_results("result-id")
        async_result.assert_called_once_with("result-id")
        self.assertEqual(scc, [1, 2, 3])
        self.assertEqual(err, [])

    @patch('core.processors.manifest.AsyncResult', return_value=MockAsyncResultPartial)
    def test_async_results_partial(self, async_result):
        scc, err = self.prc.async_results("result-id")
        async_result.assert_called_once_with("result-id")
        self.assertEqual(scc, [1, 2, 3])
        self.assertEqual(err, [4, 5])

    @patch('core.processors.manifest.AsyncResult', return_value=MockAsyncResultWaiting)
    def test_async_results_waiting(self, async_result):
        try:
            self.prc.async_results("result-id")
            self.fail("async_results did not raise when waiting for results")
        except DSProcessUnfinished:
            pass
        async_result.assert_called_once_with("result-id")

    @patch('core.processors.manifest.AsyncResult', return_value=MockAsyncResultError)
    def test_async_results_error(self, async_result):
        try:
            self.prc.async_results("result-id")
            self.fail("async_results did not raise when errors occured")
        except DSProcessError:
            pass
        async_result.assert_called_once_with("result-id")

    def test_results_success(self):
        scc, err = self.prc.results(([1, 2, 3], [],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(1, 4), scc.all()):
            self.assertIsInstance(result, Manifestation)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 3)
        self.assertEqual(err.count(), 0)

    def test_results_partial(self):
        scc, err = self.prc.results(([1, 2, 3], [4, 5],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(1, 4), scc.all()):
            self.assertIsInstance(result, Manifestation)
            self.assertEqual(result.id, index)
        for index, result in zip(range(4, 6), err.all()):
            self.assertIsInstance(result, Manifestation)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 3)
        self.assertEqual(err.count(), 2)

    def test_results_error(self):
        scc, err = self.prc.results(([], [4, 5],))
        self.assertIsInstance(scc, QuerySet)
        self.assertIsInstance(err, QuerySet)
        for index, result in zip(range(4, 6), err.all()):
            self.assertIsInstance(result, Manifestation)
            self.assertEqual(result.id, index)
        self.assertEqual(scc.count(), 0)
        self.assertEqual(err.count(), 2)

    @patch("core.processors.manifest.manifest")
    def test_manifest_from_individuals(self, manifest):
        self.prc.config = {
            "args": ["$.context"],
            "kwargs": {
                "$setting2": "$.value"
            }
        }
        individuals = Individual.objects.filter(id__in=[1, 2, 3])
        processed = self.prc.manifest_from_individuals([individual.content for individual in individuals])
        self.assertIsInstance(processed, GeneratorType)
        for individual in processed:
            self.assertIsInstance(individual, dict)
        manifest.assert_any_call("nested value", config=self.prc.config, **{"$setting2": "nested value 2"})
        manifest.assert_any_call("nested value", config=self.prc.config, **{"$setting2": "nested value 1"})
        manifest.assert_any_call("nested value", config=self.prc.config, **{"$setting2": "nested value 0"})
        self.assertEqual(manifest.call_count, 3)

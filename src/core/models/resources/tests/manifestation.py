from unittest.mock import patch

from django.test import TestCase

from core.models.resources.manifestation import Manifestation
from core.exceptions import DSProcessUnfinished
from core.tests.mocks.celery import MockAsyncResultSuccess, MockAsyncResultError, MockAsyncResultWaiting


class TestManifestationResource(TestCase):

    fixtures = ["test-manifestation"]

    def setUp(self):
        super().setUp()
        self.instance = Manifestation.objects.get(id=1)

    def test_get_data_sync(self):
        data = self.instance.get_data()
        self.assertEqual(self.instance.status, 0)
        self.assertEqual(data, [
            {"_id": 1, "context": "nested value", "number": 1, "value": "nested value 0"},
            {"_id": 3, "context": "nested value", "number": 3, "value": "nested value 2"},
        ])
        completed_at = self.instance.completed_at
        self.assertIsNotNone(completed_at)
        data = self.instance.get_data()
        self.assertEqual(data, [
            {"_id": 1, "context": "nested value", "number": 1, "value": "nested value 0"},
            {"_id": 3, "context": "nested value", "number": 3, "value": "nested value 2"},
        ])
        self.assertEqual(completed_at, self.instance.completed_at)

    @patch("core.tasks.manifestation.get_manifestation_data.delay", return_value="test-task")
    def test_get_data_async(self, task_delay):
        # Test processing
        try:
            self.instance.get_data(asynchronous=True)
            self.fail("Expected get_data to raise DSProcessUnfinished when manifesting asynchronously")
        except DSProcessUnfinished:
            pass
        self.assertEqual(self.instance.status, 8)
        task_delay.assert_called_once_with(1)
        async_result_path = "core.models.resources.manifestation.AsyncResult"
        with patch(async_result_path, return_value=MockAsyncResultWaiting) as AsyncResult:
            try:
                self.instance.get_data()
                self.fail("Expected get_data to raise DSProcessUnfinished when task incomplete")
            except DSProcessUnfinished:
                pass
            self.assertEqual(self.instance.status, 8)
            AsyncResult.assert_called_once_with("test-task")
        # Test success
        with patch(async_result_path, return_value=MockAsyncResultSuccess) as AsyncResult:
            data = self.instance.get_data()
            self.assertEqual(self.instance.status, 0)
            self.assertEqual(data, ([1, 2, 3], [],))  # weird data just comes from the mock
            AsyncResult.assert_called_once_with("test-task")

        # Resetting
        AsyncResult.reset_mock()
        self.instance.data = None
        # Test error
        with patch(async_result_path, return_value=MockAsyncResultError) as AsyncResult:
            data = self.instance.get_data()
            self.assertEqual(self.instance.status, 1)
            AsyncResult.assert_called_once_with("test-task")
            self.assertEqual(data, "Oops, something went wrong")

    def test_content(self):
        content_type, data = self.instance.content
        expected_manifestation_hash = "6eab071abbb42b649255ae8131f580986c750a5cf444166d3c1db00446ddc32a"
        self.assertEqual(content_type, "application/json")
        self.assertEqual(data, {
            "service": "/data/v1/mock/service/test-ready?setting1=const#" + expected_manifestation_hash,
            "data": [
                {"_id": 1, "context": "nested value", "number": 1, "value": "nested value 0"},
                {"_id": 3, "context": "nested value", "number": 3, "value": "nested value 2"},
            ]
        })

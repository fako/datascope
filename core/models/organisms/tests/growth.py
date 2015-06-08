from __future__ import unicode_literals, absolute_import, print_function, division
import six

from mock import patch

from django.test import TestCase

from core.models.organisms.growth import Growth, GrowthState
from core.processors.resources import HttpResourceProcessor
from core.tests.mocks.celery import (MockTask, MockAsyncResultSuccess, MockAsyncResultPartial,
                                    MockAsyncResultError, MockAsyncResultWaiting)
from core.exceptions import DSProcessError, DSProcessUnfinished
from core.tests.mocks.http import HttpResourceMock


class TestGrowth(TestCase):

    fixtures = ["test-growth"]

    @classmethod
    def setUpClass(cls):
        super(TestGrowth, cls).setUpClass()
        cls.expected_append_output = [
            {
                "ds_id": index + 3,
                "context": "nested value",
                "value": "nested value {}".format(index % 3)
            }
            for index in range(0, 9)
        ]
        cls.expected_finished_output = [
            {
                "ds_id": 2,
                "context": "nested value",
                "value": "nested value 0"
            }
        ]

    def setUp(self):
        self.new = Growth.objects.get(type="test_new")
        self.processing = Growth.objects.get(type="test_processing")
        self.finished = Growth.objects.get(type="test_finished")
        MockTask.reset_mock()
        MockAsyncResultSuccess.reset_mock()
        MockAsyncResultError.reset_mock()
        MockAsyncResultPartial.reset_mock()

    @patch('core.processors.HttpResourceProcessor._send_mass.s', return_value=MockTask)
    def test_begin(self, send_mass_s):
        self.new.begin("test", test="test")  # TODO: get arguments from configuration instead
        MockTask.delay.assert_called_once_with("test", test="test")
        self.assertEqual(self.new.result_id, "result-id")
        self.assertEqual(self.new.state, GrowthState.PROCESSING)
        self.assertFalse(self.new.is_finished)
        try:
            self.processing.begin("test", test="test")
            self.fail("Growth.begin did not warn against 'beginning' an already started growth.")
        except AssertionError:
            pass

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultPartial)
    def test_finish_with_errors(self, async_result):
        output, errors = self.processing.finish()
        self.assertTrue(async_result.called)
        self.assertTrue(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.PARTIAL)
        self.assertEqual(output.content, self.expected_append_output)
        self.assertEqual(self.processing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.processing.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_finish_without_errors(self, async_result):
        output, errors = self.processing.finish()
        self.assertTrue(async_result.called)
        self.assertTrue(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.COMPLETE)
        self.assertEqual(output.content, self.expected_append_output)
        self.assertEqual(len(errors), 0)
        self.assertEqual(self.processing.resources.count(), 0)

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultError)
    def test_finish_error(self, async_result):
        try:
            self.processing.finish()
            self.fail("Growth.finish did not raise an error when the background process failed.")
        except DSProcessError:
            pass
        self.assertTrue(async_result.called)
        self.assertFalse(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.ERROR)

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_finish_finished_and_partial(self, async_result):
        output, errors = self.finished.finish()
        self.assertFalse(async_result.called)
        self.assertTrue(self.finished.is_finished)
        self.assertEqual(self.finished.state, GrowthState.COMPLETE)
        self.assertEqual(output.content, self.expected_finished_output)
        self.assertEqual(len(errors), 0)
        self.assertEqual(self.finished.resources.count(), 0)
        self.finished.state = GrowthState.PARTIAL
        hrm = HttpResourceMock.objects.get(id=4)
        hrm.retain(self.finished)
        self.finished.save()
        output, errors = self.finished.finish()
        self.assertFalse(async_result.called)
        self.assertTrue(self.finished.is_finished)
        self.assertEqual(self.finished.state, GrowthState.PARTIAL)
        self.assertEqual(output.content, self.expected_finished_output)
        self.assertEqual(len(errors), 1)
        self.assertEqual(self.finished.resources.count(), 1)
        self.assertEqual([resource.id for resource in self.finished.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultWaiting)
    def test_finish_pending(self, async_result):
        try:
            self.processing.finish()
            self.fail("Growth.finish did not raise an exception when the background process is not ready.")
        except DSProcessUnfinished:
            pass
        self.assertTrue(async_result.called)
        self.assertFalse(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.PROCESSING)

    def test_append_to_output(self):
        qs = HttpResourceMock.objects.filter(id=1)
        self.new.append_to_output(qs)
        self.assertEqual(self.new.output.content, self.expected_append_output[:3])

    def test_prepare_process(self):
        process, method = self.new.prepare_process(self.new.process)
        self.assertIsInstance(process, HttpResourceProcessor)
        self.assertIsInstance(method, six.string_types)
        self.assertTrue(hasattr(process, method))

    def test_is_finished(self):
        self.new.state = GrowthState.COMPLETE
        self.new.save()
        self.assertTrue(self.new.is_finished)
        self.new.state = GrowthState.PROCESSING
        self.new.save()
        self.assertFalse(self.new.is_finished)
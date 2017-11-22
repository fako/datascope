from __future__ import unicode_literals, absolute_import, print_function, division

from mock import patch, Mock

from core.models.organisms.growth import Growth, GrowthState
from core.processors import HttpResourceProcessor
from core.processors.tests.mixins import TestProcessorMixin
from core.tests.mocks.celery import (MockTask, MockAsyncResultSuccess, MockAsyncResultPartial,
                                    MockAsyncResultError, MockAsyncResultWaiting)
from core.tests.mocks.http import HttpResourceMock
from core.exceptions import DSProcessError, DSProcessUnfinished


class TestGrowth(TestProcessorMixin):

    fixtures = ["test-growth"]

    @classmethod
    def setUpClass(cls):
        super(TestGrowth, cls).setUpClass()
        cls.expected_contributions = [
            {
                "context": "nested value",
                "value": "nested value {}".format(index % 3)
            }
            for index in range(0, 9)
        ]
        cls.expected_append_output = cls.expected_contributions
        cls.expected_inline_output = [
            {
                "context": "nested value",
                "value": {
                    "value": "nested value {}".format(index % 3),
                    "extra": "test {}".format(index % 3)
                }
            }
            for index in range(0, 3)
        ]
        cls.expected_finished_output = [
            {
                "context": "nested value",
                "value": "nested value 0"
            }
        ]
        cls.expected_dict_contributions = [
            {
                "value": "dict value {}".format(index),
                "type": "a pure dict"
            }
            for index in range(0, 2)
        ]
        cls.expected_update_output = [
            {
                "context": "nested value",
                "value": "nested value {}".format(index % 3),
                "extra": "test {}".format(index % 3)
            }
            for index in range(0, 3)
        ]
        cls.expected_update_output_individual = {
            'context': 'nested value',
            'extra': 'test 2',
            'value': 'nested value 2'
        }

    def setUp(self):
        self.new = Growth.objects.get(type="test_new")
        self.collective_input = Growth.objects.get(type="test_col_input")
        self.processing = Growth.objects.get(type="test_processing")
        self.finished = Growth.objects.get(type="test_finished")
        self.contributing = Growth.objects.get(type="test_contributing")
        self.contributing.append_to_output = Mock()
        self.contributing.inline_by_key = Mock()
        self.contributing.update_by_key = Mock()
        self.update = Growth.objects.get(type="test_update_individual")
        MockTask.reset_mock()
        MockAsyncResultSuccess.reset_mock()
        MockAsyncResultError.reset_mock()
        MockAsyncResultPartial.reset_mock()
        self.instance = self.new
        self.processor = HttpResourceProcessor

    def test_begin_with_individual_input_async(self):
        with patch('core.tasks.http.send.s', return_value=MockTask) as send_s:
            self.new.begin()
        MockTask.delay.assert_called_once_with(1024, 768, name="modest")
        self.assertEqual(self.new.result_id, "result-id")
        self.assertEqual(self.new.state, GrowthState.PROCESSING)
        self.assertFalse(self.new.is_finished)

    def test_begin_with_individual_input_sync(self):
        self.new.config = {"async": False}
        with patch('core.tasks.http.send.s', return_value=MockTask) as send_s:
            self.new.begin()
        MockTask.delay.assert_called_once_with(1024, 768, name="modest")
        self.assertEqual(self.new.result_id, None)
        self.assertEqual(self.new.state, GrowthState.CONTRIBUTE)
        self.assertFalse(self.new.is_finished)

    def test_begin_with_collective_input_async(self):
        with patch('core.tasks.http.send_mass.s', return_value=MockTask) as send_mass_s:
            self.collective_input.begin()
        MockTask.delay.assert_called_once_with(
            [["nested value 0"], ["nested value 1"], ["nested value 2"]],
            [{"context": "nested value"}, {"context": "nested value"}, {"context": "nested value"}]
        )
        self.assertEqual(self.collective_input.result_id, "result-id")
        self.assertEqual(self.collective_input.state, GrowthState.PROCESSING)
        self.assertFalse(self.collective_input.is_finished)

    def test_begin_with_collective_input_sync(self):
        self.collective_input.config = {"async": False}
        with patch('core.tasks.http.send_mass.s', return_value=MockTask) as send_mass_s:
            self.collective_input.begin()
        MockTask.delay.assert_called_once_with(
            [["nested value 0"], ["nested value 1"], ["nested value 2"]],
            [{"context": "nested value"}, {"context": "nested value"}, {"context": "nested value"}]
        )
        self.assertEqual(self.collective_input.result_id, None)
        self.assertEqual(self.collective_input.state, GrowthState.CONTRIBUTE)
        self.assertFalse(self.collective_input.is_finished)

    def test_begin_with_sample_size(self):
        self.skipTest("not tested")

    def test_begin_with_processing_state(self):
        try:
            self.processing.begin()
            self.fail("Growth.begin did not warn against 'beginning' an already started growth.")
        except AssertionError:
            pass

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultPartial)
    def test_finish_with_errors(self, async_result):
        output, errors = self.processing.finish("result")
        self.assertTrue(async_result.called)
        self.assertTrue(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.PARTIAL)
        self.assertEqual(list(output.content), self.expected_append_output)
        self.assertEqual(self.processing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.processing.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_finish_without_errors(self, async_result):
        output, errors = self.processing.finish("result")
        self.assertTrue(async_result.called)
        self.assertTrue(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.COMPLETE)
        self.assertEqual(list(output.content), self.expected_append_output)
        self.assertEqual(len(errors), 0)
        self.assertEqual(self.processing.resources.count(), 0)

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultError)
    def test_finish_error(self, async_result):
        try:
            self.processing.finish("result")
            self.fail("Growth.finish did not raise an error when the background process failed.")
        except DSProcessError:
            pass
        self.assertTrue(async_result.called)
        self.assertFalse(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.ERROR)

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultSuccess)
    def test_finish_finished_and_partial(self, async_result):
        output, errors = self.finished.finish("result")
        self.assertFalse(async_result.called)
        self.assertTrue(self.finished.is_finished)
        self.assertEqual(self.finished.state, GrowthState.COMPLETE)
        self.assertEqual(list(output.content), self.expected_finished_output)
        self.assertEqual(len(errors), 0)
        self.assertEqual(self.finished.resources.count(), 0)
        self.finished.state = GrowthState.PARTIAL
        hrm = HttpResourceMock.objects.get(id=4)
        hrm.retain(self.finished)
        self.finished.save()
        output, errors = self.finished.finish("result")
        self.assertFalse(async_result.called)
        self.assertTrue(self.finished.is_finished)
        self.assertEqual(self.finished.state, GrowthState.PARTIAL)
        self.assertEqual(list(output.content), self.expected_finished_output)
        self.assertEqual(len(errors), 1)
        self.assertEqual(self.finished.resources.count(), 1)
        self.assertEqual([resource.id for resource in self.finished.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult', return_value=MockAsyncResultWaiting)
    def test_finish_pending(self, async_result):
        try:
            self.processing.finish("result")
            self.fail("Growth.finish did not raise an exception when the background process is not ready.")
        except DSProcessUnfinished:
            pass
        self.assertTrue(async_result.called)
        self.assertFalse(self.processing.is_finished)
        self.assertEqual(self.processing.state, GrowthState.PROCESSING)

    def test_prepare_contributions_invalid_usage(self):
        qs = HttpResourceMock.objects.filter(id__in=[100])  # empty queryset
        contributions = self.contributing.prepare_contributions(qs)
        try:
            next(contributions)
            self.fail("Unavailable resources did yield contributions")
        except StopIteration:
            pass
        qs = HttpResourceMock.objects.filter(id__in=[1])
        contributions = self.contributing.prepare_contributions(qs)
        try:
            next(contributions)
            self.fail("Unspecified contribution field on Growth did yield contributions")
        except StopIteration:
            pass

    def test_prepare_contributions_dict_contributions(self):
        self.contributing.contribute = "ExtractProcessor.pass_resource_through"
        self.contributing.contribute_type = "Anything"
        self.contributing.save()
        qs = HttpResourceMock.objects.filter(id__in=[9, 10])
        contributions = self.contributing.prepare_contributions(qs)
        self.assertEqual(list(contributions), self.expected_dict_contributions)

    def test_prepare_contributions_list_contributions(self):
        self.contributing.contribute = "ExtractProcessor.extract_from_resource"
        self.contributing.contribute_type = "Anything"
        self.contributing.save()
        qs = HttpResourceMock.objects.filter(id__in=[1, 2, 3])
        contributions = self.contributing.prepare_contributions(qs)
        self.assertEqual(list(contributions), self.expected_contributions)

    def test_prepare_contributions_no_content(self):
        self.contributing.contribute = "ExtractProcessor.extract_from_resource"
        self.contributing.contribute_type = "Anything"
        self.contributing.save()
        qs = HttpResourceMock.objects.filter(id__in=[11])
        contributions = self.contributing.prepare_contributions(qs)
        self.assertEqual(list(contributions), [])

    @patch('core.processors.resources.AsyncResult')
    def test_none_contribution(self, async_result):
        output, errors = self.contributing.finish(([1, 2, 3], [4, 5],))
        self.assertFalse(async_result.called)
        self.assertTrue(self.contributing.is_finished)
        self.assertEqual(self.contributing.state, GrowthState.PARTIAL)
        self.assertEqual(list(output.content), [])
        self.assertEqual(self.contributing.append_to_output.call_count, 0)
        self.assertEqual(self.contributing.inline_by_key.call_count, 0)
        self.assertEqual(self.contributing.update_by_key.call_count, 0)
        self.assertEqual(self.contributing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.contributing.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult')
    def test_append_contribution(self, async_result):
        self.contributing.contribute = "ExtractProcessor.extract_from_resource"
        self.contributing.contribute_type = "Append"
        self.contributing.save()
        output, errors = self.contributing.finish(([1, 2, 3], [4, 5],))
        self.assertFalse(async_result.called)
        self.assertTrue(self.contributing.is_finished)
        self.assertEqual(self.contributing.state, GrowthState.PARTIAL)
        self.assertEqual(self.contributing.append_to_output.call_count, 1)
        args, kwargs = self.contributing.append_to_output.call_args
        contributions = args[0]
        self.assertEqual(list(contributions), self.expected_contributions)
        self.assertEqual(self.contributing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.contributing.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult')
    def test_inline_contribution(self, async_result):
        self.contributing.contribute = "ExtractProcessor.extract_from_resource"
        self.contributing.contribute_type = "Inline"
        contribution_key = "value"
        self.contributing.config = {"_inline_key": contribution_key}
        self.contributing.save()
        output, errors = self.contributing.finish(([1, 2, 3], [4, 5],))
        self.assertFalse(async_result.called)
        self.assertTrue(self.contributing.is_finished)
        self.assertEqual(self.contributing.state, GrowthState.PARTIAL)
        self.assertEqual(self.contributing.inline_by_key.call_count, 1)
        args, kwargs = self.contributing.inline_by_key.call_args
        contributions = args[0]
        self.assertEqual(list(contributions), self.expected_contributions)
        self.assertEqual(args[1], contribution_key)
        self.assertEqual(self.contributing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.contributing.resources], [error.id for error in errors])

    @patch('core.processors.resources.AsyncResult')
    def test_update_contribution(self, async_result):
        self.contributing.contribute = "ExtractProcessor.extract_from_resource"
        self.contributing.contribute_type = "Update"
        contribution_key = "value"
        self.contributing.config = {"_update_key": contribution_key}
        self.contributing.save()
        output, errors = self.contributing.finish(([1, 2, 3], [4, 5],))
        self.assertFalse(async_result.called)
        self.assertTrue(self.contributing.is_finished)
        self.assertEqual(self.contributing.state, GrowthState.PARTIAL)
        self.assertEqual(self.contributing.update_by_key.call_count, 1)
        args, kwargs = self.contributing.update_by_key.call_args
        contributions = args[0]
        self.assertEqual(list(contributions), self.expected_contributions)
        self.assertEqual(args[1], contribution_key)
        self.assertEqual(self.contributing.resources.count(), 2)
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], HttpResourceMock)
        self.assertEqual([resource.id for resource in self.contributing.resources], [error.id for error in errors])

    def test_append_to_output(self):
        qs = HttpResourceMock.objects.filter(id=1)
        contributions = self.new.prepare_contributions(qs)
        self.new.append_to_output(contributions)
        self.assertEqual(list(self.new.output.content), self.expected_append_output[:3])

    def test_inline_by_key(self):
        qs = HttpResourceMock.objects.filter(id__in=[6, 7, 8])
        contributions = self.collective_input.prepare_contributions(qs)
        self.collective_input.inline_by_key(contributions, "value")
        self.assertEqual(list(self.collective_input.output.content), self.expected_inline_output)
        self.assertEqual(self.collective_input.output.identifier, "value.value")

    def test_update_collective_by_key(self):
        qs = HttpResourceMock.objects.filter(id__in=[6, 7, 8])
        contributions = self.collective_input.prepare_contributions(qs)
        self.collective_input.update_by_key(contributions, "value")
        self.assertEqual(list(self.collective_input.output.content), self.expected_update_output)
        self.assertEqual(
            self.collective_input.output.identifier,
            "value"  # doesn't update in contrast to inline_by_key
        )

    def test_update_individual_by_key(self):
        qs = HttpResourceMock.objects.filter(id__in=[6, 7, 8])
        contributions = self.collective_input.prepare_contributions(qs)
        self.update.update_by_key(contributions, "value")
        self.assertEqual(self.update.output.content, self.expected_update_output_individual)

    def test_is_finished(self):
        self.new.state = GrowthState.COMPLETE
        self.new.save()
        self.assertTrue(self.new.is_finished)
        self.new.state = GrowthState.PROCESSING
        self.new.save()
        self.assertFalse(self.new.is_finished)

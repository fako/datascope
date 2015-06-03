from __future__ import unicode_literals, absolute_import, print_function, division
import six

from mock import MagicMock, patch

from django.test import TestCase

from core.models.organisms.growth import Growth, GrowthState
from core.processors.resources import HttpResourceProcessor
from core.tests.mocks import MockTask


class TestGrowth(TestCase):

    fixtures = ["test-growth"]

    def setUp(self):
        self.new = Growth.objects.get(type="test_new")
        MockTask.reset_mock()

    @patch('core.processors.HttpResourceProcessor._send_mass.s', return_value=MockTask)
    def test_begin(self, send_mass_s):
        self.new.begin("test", test="test")
        MockTask.delay.assert_called_once_with("test", test="test")
        self.assertEqual(self.new.task_id, "task-id")
        self.assertEqual(self.new.status, GrowthState.PROCESSING)
        self.assertFalse(self.new.is_finished)

    def test_prepare_process(self):
        process, method = self.new.prepare_process(self.new.process)
        self.assertIsInstance(process, HttpResourceProcessor)
        self.assertIsInstance(method, six.string_types)
        self.assertTrue(hasattr(process, method))

    def test_is_finished(self):
        self.new.state = GrowthState.FINISHED
        self.new.save()
        self.assertTrue(self.new.is_finished)
        self.new.state = GrowthState.PROCESSING
        self.new.save()
        self.assertFalse(self.new.is_finished)

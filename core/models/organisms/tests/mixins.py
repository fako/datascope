from __future__ import unicode_literals, absolute_import, print_function, division

from types import MethodType

from django.test import TestCase
from celery.canvas import Signature

from core.processors.resources import HttpResourceProcessor
from core.processors.base import ArgumentsTypes


class TestProcessorMixin(TestCase):

    def test_prepare_process_async(self):
        process, method, args_type = self.instance.prepare_process(self.instance.process, async=True)
        self.assertIsInstance(process, HttpResourceProcessor)
        self.assertTrue(callable(method))
        self.assertIsInstance(method, MethodType)  # 'delay' method of the Signature class

    def test_prepare_process_sync(self):
        process, method, args_type = self.instance.prepare_process(self.instance.process, async=False)
        self.assertIsInstance(process, HttpResourceProcessor)
        self.assertTrue(callable(method))
        self.assertIsInstance(method, Signature)  # the callable 'Signature' is a sync version of a task

    def test_prepare_process_batch(self):
        for batch_method in self.processor.ARGS_BATCH_METHODS:
            process, method, args_type = self.instance.prepare_process(
                "{}.{}".format(self.processor.__name__, batch_method),
                async=False
            )
            self.assertEqual(args_type, ArgumentsTypes.BATCH)

    def test_prepare_process_normal(self):
        for normal_method in [cll for cll in self.processor.__dict__.keys() if callable(cll)]:
            print(normal_method)
            process, method, args_type = self.instance.prepare_process(
                "{}.{}".format(self.processor.__name__, normal_method),
                async=True
            )
            self.assertEqual(args_type, ArgumentsTypes.NORMAL)

    def test_config(self):
        self.instance.config = {"test": "config"}
        process, method, args_type = self.instance.prepare_process(self.instance.process, async=True)
        self.assertEqual(process.config.test, "config")

from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from core.processors.compare import ComparisonProcessor
from core.models import Individual


class TestHttpPrivateResourceProcessor(TestCase):

    def test_get_session(self):
        self.skipTest("not tested")

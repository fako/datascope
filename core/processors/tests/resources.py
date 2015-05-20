from django.test import TestCase

from datascope.configuration import MOCK_CONFIGURATION
from core.processors.resources import HttpResourceProcessor
from core.utils.configuration import ConfigurationType


class TestFetch(TestCase):

    def setUp(self):
        super(TestFetch, self).setUp()
        self.config = ConfigurationType(namespace="name", private=["_test3"], defaults=MOCK_CONFIGURATION)
        self.config.set_configuration({
            "test": "public",
            "_test2": "protected",
            "_test3": "private"
        })

    def test_single_fetch(self):
        pass

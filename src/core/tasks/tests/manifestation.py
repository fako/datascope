from django.test import TestCase

from core.models.resources.manifestation import Manifestation
from core.tasks import get_manifestation_data


class TestManifestationTasks(TestCase):

    fixtures = ["test-manifestation"]

    def setUp(self):
        super().setUp()
        self.config = {
            "community": "CommunityMock",
            "_namespace": "manifestation_test",
            "_private": []
        }

    def test_get_manifestation_data(self):
        self.assertTrue(hasattr(get_manifestation_data, "delay"))
        manifestation_data = get_manifestation_data(1)
        self.assertIsInstance(manifestation_data, list)
        self.assertEqual(manifestation_data, [
            {"_id": 1, "context": "nested value", "number": 1, "value": "nested value 0"},
            {"_id": 3, "context": "nested value", "number": 3, "value": "nested value 2"},
        ])
        manifestation_data = get_manifestation_data(2)
        self.assertIsInstance(manifestation_data, list)
        self.assertEqual(manifestation_data, [
            {"_id": 1, "context": "nested value", "number": 1, "value": "nested value 0"},
            {"_id": 2, "context": "nested value", "number": 2, "value": "nested value 1"},
            {"_id": 3, "context": "nested value", "number": 3, "value": "nested value 2"},
        ])
        try:
            get_manifestation_data(666)
            self.fail("Missing manifestation did not raise NotFound")
        except Manifestation.DoesNotExist:
            pass

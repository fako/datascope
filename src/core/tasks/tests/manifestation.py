from mock import patch

from django.test import TestCase

from core.models.resources.manifestation import Manifestation
from core.tasks import get_manifestation_data, manifest, manifest_serie


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

    def test_manifest(self):
        self.assertTrue(hasattr(manifest, "delay"))
        scc, err = manifest("test-ready", setting1="const", config=self.config)
        self.assertEqual(scc, [1])
        self.assertEqual(err, [])
        scc, err = manifest("test-ready", config=self.config, **{
            "setting1": "const",
            "$setting2": "override",
            "ignored": True,
        })
        self.assertEqual(scc, [2])
        self.assertEqual(err, [])
        scc, err = manifest("test-ready", config=self.config, **{
            "setting1": "const",
            "$setting2": "new",
            "ignored": True,
        })
        latest = Manifestation.objects.latest()
        self.assertEqual(scc, [latest.id])
        self.assertEqual(err, [])
        self.assertEqual(getattr(latest.config, "$setting2"), "new")

    @patch("core.models.resources.manifestation.Manifestation.get_data", side_effect=Exception("Error"))
    def test_manifest_error(self, get_data):
        scc, err = manifest("does-not-exist", config=self.config)
        self.assertEqual(scc, [])
        self.assertEqual(err, [])
        scc, err = manifest("test-ready", setting1="const", config=self.config)
        self.assertEqual(scc, [])
        self.assertEqual(err, [1])
        scc, err = manifest("test-ready", config=self.config, **{
            "setting1": "const",
            "$setting2": "new",
            "ignored": True,
        })
        latest = Manifestation.objects.latest()
        self.assertEqual(getattr(latest.config, "$setting2"), "new")
        self.assertEqual(scc, [])
        self.assertEqual(err, [latest.id])

    def test_manifest_serie(self):
        scc, err = manifest_serie(
            [
                ("test-ready",),
                ("test-ready",),
                ("test-ready",),
                ("does-not-exist",)
            ],
            [
                {
                    "setting1": "const"
                },
                {
                    "setting1": "const",
                    "$setting2": "override",
                    "ignored": True,
                },
                {
                    "setting1": "const",
                    "$setting2": "new",
                    "ignored": True,
                },
                {
                    "setting1": "const"
                },
            ],
            config=self.config
        )
        latest = Manifestation.objects.latest()
        self.assertEqual(getattr(latest.config, "$setting2"), "new")
        self.assertEqual(scc, [1, 2, latest.id])
        self.assertEqual(err, [])

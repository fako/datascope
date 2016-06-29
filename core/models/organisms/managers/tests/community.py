from __future__ import unicode_literals

from django.test import TestCase

from core.tests.mocks.community import CommunityMock


class TestCommunityManager(TestCase):

    fixtures = ["test-community"]

    def test_get_by_signature(self):
        # Static config with an illegal key
        constant_config = {
            "setting1": "const",
            "illegal": "please"
        }
        signature = CommunityMock.get_signature_from_input("test", **constant_config)
        community = CommunityMock.objects.get_by_signature(signature, **constant_config)
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertEqual(community.config.setting1, "const")
        self.assertFalse(hasattr(community.config, "illegal"))
        # Variable config
        variable_config = {
            "$setting2": "variable"
        }
        signature = CommunityMock.get_signature_from_input("test", **variable_config)
        community = CommunityMock.objects.get_by_signature(signature, **variable_config)
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertTrue(hasattr(community.config, "$setting2"))
        # Non existant config
        non_existant = {
            "setting1": "variable",
        }
        signature = CommunityMock.get_signature_from_input("test", **non_existant)
        try:
            CommunityMock.objects.get_by_signature(signature, **non_existant)
            self.fail("CommunityManager.get_by_signature did not raise with non-existant community")
        except CommunityMock.DoesNotExist:
            pass

    def test_get_or_create_by_signature(self):
        # Static config with an illegal key
        constant_config = {
            "setting1": "const",
            "illegal": "please"
        }
        signature = CommunityMock.get_signature_from_input("test", **constant_config)
        community, created = CommunityMock.objects.get_or_create_by_signature(signature, **constant_config)
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertFalse(created)
        self.assertEqual(community.config.setting1, "const")
        self.assertFalse(hasattr(community.config, "illegal"))
        # Variable config
        variable_config = {
            "$setting2": "variable"
        }
        signature = CommunityMock.get_signature_from_input("test", **variable_config)
        community, created = CommunityMock.objects.get_or_create_by_signature(signature, **variable_config)
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertFalse(created)
        self.assertTrue(hasattr(community.config, "$setting2"))
        # Non existant config
        non_existant = {
            "setting1": "created",
        }
        signature = CommunityMock.get_signature_from_input("test", **non_existant)
        community, created = CommunityMock.objects.get_or_create_by_signature(signature, **non_existant)
        self.assertIsNotNone(community)
        self.assertIsNotNone(community.id)
        self.assertTrue(created)
        self.assertEqual(community.config.setting1, "created")

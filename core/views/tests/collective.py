from __future__ import unicode_literals, absolute_import, print_function, division

import json

from django.test import TestCase, Client


class TestCollectiveView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollectiveView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/collective/{}/"


    def test_get(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        response = self.client.get(self.test_url.format(2))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)


class TestCollectiveContentView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollectiveContentView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/collective/{}/content/"

    def test_get(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertTrue(data)
        response = self.client.get(self.test_url.format(2))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)

    def test_post(self):
        self.skipTest("not tested")

from __future__ import unicode_literals, absolute_import, print_function, division

import json

from django.test import TestCase, Client


class TestIndividualView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestIndividualView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/individual/{}/"


    def test_get(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertIn("properties", data)
        response = self.client.get(self.test_url.format(9))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)


class TestIndividualContentView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestIndividualContentView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/individual/{}/content/"

    def test_get(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertTrue(data)
        response = self.client.get(self.test_url.format(9))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)

from __future__ import unicode_literals, absolute_import, print_function, division

import json

from django.test import TestCase, Client

from core.models import Collective


class TestCollectiveView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollectiveView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/collective/{}/"

    def test_get(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIsInstance(data, dict)
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        response = self.client.get(self.test_url.format(3))
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)


class TestCollectiveContentView(TestCase):

    fixtures = ["test-organisms"]

    def setUp(self):
        super(TestCollectiveContentView, self).setUp()
        self.client = Client()
        self.test_url = "/data/v1/collective/{}/content/"

    def test_get_success(self):
        response = self.client.get(self.test_url.format(1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertTrue(data)

    def test_get_not_found(self):
        response = self.client.get(self.test_url.format(3))
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)

    def test_post_success(self):
        additions = Collective.objects.get(id=1)
        response = self.client.post(
            self.test_url.format(1),
            data=json.dumps(list(additions.content)),
            content_type="application/json"
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Added 3 individuals")

    def test_post_schema_error(self):
        additions = Collective.objects.get(id=1)
        response = self.client.post(
            self.test_url.format(2),
            data=json.dumps(list(additions.content)),
            content_type="application/json"
        )
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(data, dict)
        self.assertIn("detail", data)
        self.assertEqual(data["detail"]["message"], "Additional properties are not allowed ('context' was unexpected)")
        self.assertIsInstance(data["detail"]["schema"], dict)

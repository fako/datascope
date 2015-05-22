import json
from copy import deepcopy

from django.core.exceptions import ValidationError

from core.models.resources.tests.http import HttpResourceTestMixin, ConfigurationFieldTestMixin
from core.tests.mocks import MOCK_DATA

from sources.models.local import HttpResourceMock


class TestHttpResourceMock(HttpResourceTestMixin, ConfigurationFieldTestMixin):

    fixtures = ['test-http-resource-mock']

    @staticmethod
    def get_test_instance():
        return HttpResourceMock()

    def fill_test_instance(self):
        self.instance.uri = "uri"
        self.instance.data_hash = "12345"
        self.instance.head = {"json": "test"}
        self.instance.body = "response"
        self.instance.status = 200

    def setUp(self):
        super(TestHttpResourceMock, self).setUp()
        self.content_type_header = {
            "content-type": "application/json"  # change to Accept
        }
        self.test_get_request = {
            "args": ("en", "test",),
            "kwargs": {},
            "method": "get",
            "url": "http://localhost:8000/en/?q=test",
            "headers": {"Accept": "application/json"},
            "data": None,
        }
        self.test_post_request = {
            "args": ("en", "test",),
            "kwargs": {"query": "test"},
            "method": "post",
            "url": "http://localhost:8000/en/?q=test",
            "headers": {"Accept": "application/json"},
            "data": {"test": "test"}
        }

    def assert_call_args_get(self, call_args, term):
        expected_url = "http://localhost:8000/en/?q={}&key=oehhh&auth=1".format(term)
        args, kwargs = call_args
        preq = args[0]
        self.assertTrue(preq.url.startswith("http://localhost:8000/en/?"))
        self.assertIn("q={}".format(term), preq.url)
        self.assertIn("key=oehhh", preq.url)
        self.assertIn("auth=1", preq.url)
        self.assertEqual(len(expected_url), len(preq.url))
        self.assertEqual(preq.headers, {"Accept": "application/json"})

    def assert_call_args_post(self, call_args, term):
        expected_url = "http://localhost:8000/en/?q={}&key=oehhh&auth=1".format(term)
        expected_body = "test={}".format(term)
        args, kwargs = call_args
        preq = args[0]
        self.assertTrue(preq.url.startswith("http://localhost:8000/en/?"))
        self.assertIn("q={}".format(term), preq.url)
        self.assertIn("key=oehhh", preq.url)
        self.assertIn("auth=1", preq.url)
        self.assertEqual(len(expected_url), len(preq.url))
        self.assertEqual(preq.headers, {"Accept": "application/json"})
        self.assertEqual(preq.body, expected_body)

    def test_get_new(self):
        # Make a new request and store it.
        instance = self.model().get("new")
        instance.save()
        self.assert_call_args_get(instance.session.send.call_args, "new")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Make a new request from an existing request dictionary
        request = self.model().get("new2").request
        instance = self.model(request=request).get()
        instance.save()
        self.assert_call_args_get(instance.session.send.call_args, "new2")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_get_success(self):
        # Load an existing request
        instance = self.model().get("success")
        self.assertFalse(instance.session.send.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assertFalse(instance.session.send.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_get_retry(self):
        # Load and retry an existing request
        instance = self.model().get("fail")
        self.assert_call_args_get(instance.session.send.call_args, "fail")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assert_call_args_get(instance.session.send.call_args, "fail")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_get_invalid(self):
        # Invalid invoke of get
        try:
            self.model().get()
            self.fail("Get did not raise a validation exception when invoked with invalid arguments.")
        except ValidationError:
            pass
        # Invalid request preset
        self.test_get_request["args"] = tuple()
        try:
            self.model(request=self.test_get_request).get()
            self.fail("Get did not raise a validation exception when confronted with an invalid preset request.")
        except ValidationError:
            pass

    def test_post_new(self):
        # Make a new request and store it.
        instance = self.model().get("new")
        instance.save()
        self.assert_call_args(instance.session.send.call_args, "new")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Make a new request from an existing request dictionary
        request = self.model().get("new2").request
        instance = self.model(request=request).get()
        instance.save()
        self.assert_call_args(instance.session.send.call_args, "new2")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_post_success(self):
        # Load an existing request
        instance = self.model().get("success")
        self.assertFalse(instance.session.send.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assertFalse(instance.session.send.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_post_retry(self):
        # Load and retry an existing request
        instance = self.model().get("fail")
        self.assert_call_args(instance.session.send.call_args, "fail")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assert_call_args(instance.session.send.call_args, "fail")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_post_invalid(self):
        # Invalid invoke of get
        try:
            self.model().get()
            self.fail("Get did not raise a validation exception when invoked with invalid arguments.")
        except ValidationError:
            pass
        # Invalid request preset
        self.test_request["args"] = tuple()
        try:
            self.model(request=self.test_request).get()
            self.fail("Get did not raise a validation exception when confronted with an invalid preset request.")
        except ValidationError:
            pass

    def test_request_with_auth(self):
        self.instance.request = self.test_post_request
        request = self.instance.request_with_auth()
        self.assertIn("auth=1", request["url"])
        self.assertNotIn("auth=1", self.instance.request["url"], "request_with_auth should not alter existing request")
        self.assertIn("key=oehhh", request["url"])
        self.assertNotIn("key=oehhh", self.instance.request["url"], "request_with_auth should not alter existing request")
        self.assertEqual(request["data"], self.test_post_request["data"])

    def test_request_without_auth(self):
        self.instance.request = deepcopy(self.test_post_request)
        self.instance.request["url"] = self.test_post_request["url"] + "&auth=1&key=ahhh"
        request = self.instance.request_without_auth()
        self.assertNotIn("auth=1", request["url"])
        self.assertIn("auth=1", self.instance.request["url"], "request_without_auth should not alter existing request")
        self.assertNotIn("key=oehhh", request["url"])
        self.assertIn("key=ahhh", self.instance.request["url"], "request_without_auth should not alter existing request")
        self.assertEqual(request["data"], self.test_post_request["data"])

    def test_create_next_request(self):
        instance = self.model().get("next")
        request = instance.create_next_request()
        self.assertIn("next=1", request["url"])
        self.assertNotIn("auth=1", instance.request["url"], "create_next_request should not alter existing request")
        instance = self.model().post("next")
        request = instance.create_next_request()
        self.assertIn("next=1", request["url"])
        self.assertNotIn("auth=1", instance.request["url"], "create_next_request should not alter existing request")

    def test_validate_request_args(self):
        # Valid
        try:
            self.instance.validate_request(self.test_get_request)
        except ValidationError:
            self.fail("validate_request raised for a valid request.")
        # Invalid
        invalid_request = deepcopy(self.test_get_request)
        invalid_request["args"] = ("en", "en", "test")
        try:
            self.instance.validate_request(invalid_request)
            self.fail("validate_request did not raise with invalid args for schema.")
        except ValidationError:
            pass
        invalid_request["args"] = tuple()
        try:
            self.instance.validate_request(invalid_request)
            self.fail("validate_request did not raise with invalid args for schema.")
        except ValidationError:
            pass
        # No schema
        self.instance.GET_SCHEMA["args"] = None
        try:
            self.instance.validate_request(self.test_get_request)
            self.fail("validate_request did not raise with invalid args for no schema.")
        except ValidationError:
            pass
        # Always valid schema
        self.instance.GET_SCHEMA["args"] = {}
        try:
            self.instance.validate_request(invalid_request)
        except ValidationError:
            self.fail("validate_request invalidated with a schema without restrictions.")

    def test_validate_request_kwargs(self):
        # Valid
        try:
            self.instance.validate_request(self.test_request)
        except ValidationError:
            self.fail("validate_request raised for a valid request.")
        # Invalid
        invalid_request = deepcopy(self.test_request)
        invalid_request["args"] = ("en", "en", "test")
        try:
            self.instance.validate_request(invalid_request)
            self.fail("validate_request did not raise with invalid args for schema.")
        except ValidationError:
            pass
        invalid_request["args"] = tuple()
        try:
            self.instance.validate_request(invalid_request)
            self.fail("validate_request did not raise with invalid args for schema.")
        except ValidationError:
            pass
        # No schema
        self.instance.GET_SCHEMA["args"] = None
        try:
            self.instance.validate_request(self.test_request)
            self.fail("validate_request did not raise with invalid args for no schema.")
        except ValidationError:
            pass
        # Always valid schema
        self.instance.GET_SCHEMA["args"] = {}
        try:
            self.instance.validate_request(invalid_request)
        except ValidationError:
            self.fail("validate_request invalidated with a schema without restrictions.")

    def test_clean_get(self):
        self.instance.request = self.test_get_request
        self.instance.clean()
        self.assertEqual(self.instance.uri, "localhost:8000/en/?q=test")
        self.assertEqual(self.instance.data_hash, "")

    def test_clean_post(self):
        self.instance.request = self.test_post_request
        self.instance.clean()
        self.assertEqual(self.instance.uri, "localhost:8000/en/?q=test")
        self.assertEqual(self.instance.data_hash, "31ead60c9066eefb8011f3f68aed25d004d60957")

    def test_query(self):
        instance = self.model()
        self.assertIsNone(instance.query)
        instance.get("new")
        self.assertEqual(instance.query, "new")

    def test_input_for_organism(self):
        instance = self.model()
        spirit, content_type, data = instance.input_for_organism
        self.assertIsNone(spirit)
        self.assertIsNone(content_type)
        self.assertIsNone(data)
        instance.get("new")
        spirit, content_type, data = instance.input_for_organism
        self.assertEqual(spirit, "new")
        self.assertEqual(content_type, "application/json")
        self.assertEqual(data, MOCK_DATA)
        instance.post("new")
        spirit, content_type, data = instance.input_for_organism
        self.assertEqual(spirit, "new")
        self.assertEqual(content_type, "application/json")
        self.assertEqual(data, MOCK_DATA)

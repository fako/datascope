import json
from copy import deepcopy

from django.test import TestCase
from django.core.exceptions import ValidationError

from core.exceptions import DSHttpError50X, DSHttpError40X
from core.models.resources.http import HttpResource, HttpResourceMock
from core.utils.mocks import MOCK_DATA


class HttpResourceTestMixin(TestCase):

    def setUp(self):
        super(HttpResourceTestMixin, self).setUp()
        self.instance = self.get_test_instance()
        self.test_data = {"data": "test"}


    @staticmethod
    def get_test_instance():
        raise NotImplementedError()

    def test_data(self):
        # Test access when request is missing
        content_type, data = self.instance.data
        self.assertIsNone(content_type)
        self.assertIsNone(data)
        # Test when request was made
        self.instance.head = {"Content-Type": "application/json; charset=utf-8"}
        self.instance.body = json.dumps(self.test_data)
        self.instance.status = 200
        content_type, data = self.instance.data
        self.assertEqual(content_type, "application/json")
        self.assertEqual(data, self.test_data)


    def test_parameters(self):
        self.assertIsInstance(self.instance.parameters(), dict)

    def test_auth_parameters(self):
        self.assertIsInstance(self.instance.auth_parameters(), dict)

    def test_next_parameters(self):
        self.assertIsInstance(self.instance.next_parameters(), dict)

    def test_make_request(self):
        test_url = "http://localhost:8000/test/"
        content_header = {
            "Accept": "application/json"
        },
        self.instance.request = {
            "args": tuple(),
            "kwargs": {},
            "method": "get",
            "url": test_url,
            "headers": content_header,
            "data": {},
        }
        self.instance._make_request()

        args, kwargs = self.instance.session.get.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["headers"], content_header)

        self.assertEqual(self.instance.head, {"Content-Type": "application/json"})
        self.assertEqual(self.instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(self.instance.status, 200)

        self.instance.request = None
        try:
            self.instance._make_request()
            self.fail("_make_request should fail when self.request is not set.")
        except AssertionError:
            pass

    def test_success(self):
        success_range = range(200, 209)
        for status in range(0, 999):
            self.instance.status = status
            if status in success_range:
                self.assertTrue(self.instance.success, "Success property is not True with status={}".format(status))
            else:
                self.assertFalse(self.instance.success, "Success property is not False with status={}".format(status))

    def test_handle_error(self):
        statuses_50x = range(500, 505)
        statuses_40x = range(400, 410)
        for status in statuses_50x:
            self.instance.status = status
            try:
                self.instance._handle_errors()
                self.fail("Handle error doesn't handle status {}".format(status))
            except DSHttpError50X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 50X".format(exception))
        for status in statuses_40x:
            self.instance.status = status
            try:
                self.instance._handle_errors()
                self.fail("Handle error doesn't handle status {}".format(status))
            except DSHttpError40X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 40X".format(exception))

    def test_uri_from_url(self):
        uri = HttpResource.uri_from_url("http://localhost:8000/")
        self.assertEqual(uri, "localhost:8000/")
        uri = HttpResource.uri_from_url("https://localhost:8000/")
        self.assertEqual(uri, "localhost:8000/")

    def test_hash_from_data(self):
        # Give no data
        post_data = HttpResource.hash_from_data({})
        self.assertEqual(post_data, "")
        # Give data
        post_data = HttpResource.hash_from_data(self.test_data)
        self.assertIsInstance(post_data, str)
        # Compare with slightly altered data
        self.test_data["data"] = "tezt"
        post_data2 = HttpResource.hash_from_data(self.test_data)
        self.assertNotEqual(post_data, post_data2)


class ConfigurationFieldTestMixin(TestCase):

    def setUp(self):
        super(ConfigurationFieldTestMixin, self).setUp()
        self.instance = self.get_test_instance()
        self.model = self.instance.__class__

    @staticmethod
    def get_test_instance():
        raise NotImplementedError("Should return the model that holds the configuration field.")

    def fill_test_instance(self):
        raise NotImplementedError("Should make self.instance ready for save by filling required fields.")

    def test_set_storage_load_and_get(self):
        self.fill_test_instance()
        self.instance.config = {"test": "loaded"}
        self.assertEqual(self.instance.config.test, "loaded")
        self.instance.save()
        new = self.model.objects.get(id=self.instance.id)
        self.assertEqual(new.config.test, "loaded")


class TestHttpResource(HttpResourceTestMixin, ConfigurationFieldTestMixin):

    fixtures = ['test-http-resource-mock']

    @staticmethod
    def get_test_instance():
        return HttpResourceMock()

    def fill_test_instance(self):
        self.instance.uri = "uri"
        self.instance.post_data = "12345"
        self.instance.head = {"json": "test"}
        self.instance.body = "response"
        self.instance.status = 200

    def setUp(self):
        super(TestHttpResource, self).setUp()
        self.content_type_header = {
            "Content-Type": "application/json"  # change to Accept
        }
        self.test_request = {
            "args": ("en", "test",),
            "kwargs": {},
            "method": "get",
            "url": "http://localhost:8000/en/?q=test",
            "headers": {"Accept": "application/json"},
            "data": {},
        }

    def assert_call_args(self, call_args, term):
        expected_url = "http://localhost:8000/en/?q={}&key=oehhh&auth=1".format(term)
        args, kwargs = call_args
        url = args[0]
        self.assertTrue(url.startswith("http://localhost:8000/en/?"))
        self.assertIn("q={}".format(term), url)
        self.assertIn("key=oehhh", url)
        self.assertIn("auth=1", url)
        self.assertEqual(len(expected_url), len(url))
        self.assertEqual(kwargs["headers"], {"Accept": "application/json"})

    def test_get_new(self):
        # Make a new request and store it.
        instance = self.model().get("new")
        instance.save()
        self.assert_call_args(instance.session.get.call_args, "new")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Make a new request from an existing request dictionary
        request = self.model().get("new2").request
        instance = self.model(request=request).get()
        instance.save()
        self.assert_call_args(instance.session.get.call_args, "new2")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_get_success(self):
        # Load an existing request
        instance = self.model().get("success")
        self.assertFalse(instance.session.get.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assertFalse(instance.session.get.called)
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)

    def test_get_retry(self):
        # Load and retry an existing request
        instance = self.model().get("fail")
        self.assert_call_args(instance.session.get.call_args, "fail")
        self.assertEqual(instance.head, self.content_type_header)
        self.assertEqual(instance.body, json.dumps(MOCK_DATA))
        self.assertEqual(instance.status, 200)
        self.assertTrue(instance.id)
        # Load an existing resource from its request
        request = instance.request
        instance = self.model(request=request).get()
        self.assert_call_args(instance.session.get.call_args, "fail")
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
        self.test_request["args"] = tuple()
        try:
            self.model(request=self.test_request).get()
            self.fail("Get did not raise a validation exception when confronted with an invalid preset request.")
        except ValidationError:
            pass

    def test_request_with_auth(self):
        self.instance.request = self.test_request
        request = self.instance.request_with_auth()
        self.assertIn("auth=1", request["url"])
        self.assertNotIn("auth=1", self.instance.request["url"], "request_with_auth should not alter existing request")
        self.assertIn("key=oehhh", request["url"])
        self.assertNotIn("key=oehhh", self.instance.request["url"], "request_with_auth should not alter existing request")

    def test_request_without_auth(self):
        self.instance.request = deepcopy(self.test_request)
        self.instance.request["url"] = self.test_request["url"] + "&auth=1&key=ahhh"
        request = self.instance.request_without_auth()
        self.assertNotIn("auth=1", request["url"])
        self.assertIn("auth=1", self.instance.request["url"], "request_without_auth should not alter existing request")
        self.assertNotIn("key=oehhh", request["url"])
        self.assertIn("key=ahhh", self.instance.request["url"], "request_without_auth should not alter existing request")

    def test_create_next_request(self):
        instance = self.model().get("success")
        request = instance.create_next_request()
        self.assertIn("next=1", request["url"])
        self.assertNotIn("auth=1", instance.request["url"], "create_next_request should not alter existing request")

    def test_validate_request_args(self):
        # Valid
        try:
            self.instance.validate_request(self.test_request)
        except ValidationError as ex:
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

    def test_clean(self):
        self.instance.request = self.test_request
        self.instance.clean()
        self.assertEqual(self.instance.uri, "localhost:8000/en/?q=test")
        self.assertEqual(self.instance.post_data, "")

import json

from django.test import TestCase

from core.exceptions import DSHttpError50X, DSHttpError40X
from core.models.resources.http import HttpResource


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
        # See if request was made properly
        args, kwargs = self.instance.session.get.call_args
        self.assertEqual(args[0], test_url)
        self.assertEqual(kwargs["headers"], content_header)
        # Make sure that response fields are set to something and do not remain None
        self.assertIsNotNone(self.instance.head)
        self.assertIsNotNone(self.instance.body)
        self.assertIsNotNone(self.instance.status)
        # Make sure that make request aborts with no request
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




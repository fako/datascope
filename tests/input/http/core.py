import json

from django.test import TestCase
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from mock import Mock

from HIF.input.http.core import HttpLink
from HIF.exceptions import HIFHttpError40X, HIFHttpError50X, HIFCouldNotLoadFromStorage


def load_fail():
    raise HIFCouldNotLoadFromStorage


class TestHttpLink(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_response = {
            "response_from_test": "test"
        }
        def test_callable():
            return "test"
        cls.parameters = {
            "test-static": "test",
            "test-callable": test_callable
        }
        cls.init_dict = {
            "head": "",
            "body": json.dumps(cls.test_response),
            "status": 0,
            "retained": False,
            "type": "DataLink",
            "identifier": "",
        }
        cls.methods_get_uses = ['prepare_link','enable_auth','load','send_request','handle_error', "store_response"]
        cls.test_url = "http://localhost:8000/test/"

    def setup_mock_methods(self, http_link):
        for method in self.methods_get_uses:
            if method in ["success"]: continue
            setattr(http_link,method,Mock(return_value=True))
        return http_link

    def check_method_usage(self, http_link, methods_not_to_call):
        for method in self.methods_get_uses:
            if method in ["success"]: continue
            mock_method = getattr(http_link, method)
            if method in methods_not_to_call:
                self.assertFalse(mock_method.called,"{} method shouldn't have been called".format(method))
            else:
                self.assertTrue(mock_method.called,"{} method should have been called".format(method))


    def test_get_method_normal_execution(self):
        """
        This test tests the call of get
        It should call many other methods
        """
        # Test vars
        methods_not_to_call = []

        # Setup class
        http_link = HttpLink(**self.init_dict)
        http_link = self.setup_mock_methods(http_link)
        http_link.load.side_effect = load_fail

        # Make call and test
        link = http_link.get()
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link,methods_not_to_call)


    def test_get_method_second_execution(self):
        """
        Test get again
        This time it should return cached results without calling functions.
        """
        # Test vars
        methods_not_to_call = self.methods_get_uses

        # Setup class
        http_link = HttpLink(**self.init_dict)
        http_link = self.setup_mock_methods(http_link)
        http_link.status = 200

        # Call and test
        link = http_link.get()
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link, methods_not_to_call)

    def test_get_method_second_execution_refresh(self):
        """
        This test tests the call of get second time with refresh=True
        It should call many other methods
        """
        # Test vars
        methods_not_to_call = []

        # Setup class
        http_link = HttpLink(**self.init_dict)
        http_link = self.setup_mock_methods(http_link)
        http_link.load.side_effect = load_fail
        http_link.status = 200

        # Make call and test
        link = http_link.get(refresh=True)
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link, methods_not_to_call)

    def test_get_method_load_from_database(self):
        """
        This test tests the call of get
        It checks whether methods that could get skipped after db result get skipped
        """
        # Test vars
        methods_not_to_call = ["send_request","handle_error","store_response"]

        # Setup class
        http_link = HttpLink(**self.init_dict)
        http_link = self.setup_mock_methods(http_link)
        http_link.success = Mock(return_value=True) # we force that results loaded will be success

        link = http_link.get(refresh=True) # we force that a fetch attempt is made despite success=True
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link,methods_not_to_call)

    def test_prepare_link_method(self):
        """
        Tests whether the link is appended with parameters
        And is valid
        """
        http_link = HttpLink(**self.init_dict)
        http_link.HIF_link = self.test_url
        http_link.HIF_parameters = self.parameters
        http_link.prepare_link()
        self.assertIn("?",http_link.url)
        self.assertIn("test-static=test",http_link.url)
        self.assertIn("test-callable=test",http_link.url)
        try:
            validator = URLValidator()
            validator(http_link.url)
        except ValidationError:
            self.fail("{} by prepare_link did not validate.".format(http_link.url))

    def test_enable_auth_method(self):
        """
        Enable auth should set the link that send_request will use.
        """
        http_link = HttpLink(**self.init_dict)
        http_link._link = self.test_url
        http_link.enable_auth()
        self.assertEqual(self.test_url, http_link.url)

    def test_store_response_function(self):
        http_link = HttpLink(**self.init_dict)
        http_link.status = 200
        http_link.cache = False
        self.assertFalse(http_link.store_response())
        http_link.cache = True
        self.assertTrue(http_link.store_response())
        http_link.status = 500
        self.assertTrue(http_link.store_response())

    def test_handle_error_method(self):
        statuses_50X = range(500,505)
        statuses_40X = range(400,410)
        http_link = HttpLink(**self.init_dict)
        for status in statuses_50X:
            http_link.status = status
            try:
                http_link.handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except HIFHttpError50X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 50X".format(exception))
        for status in statuses_40X:
            http_link.status = status
            try:
                http_link.handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except HIFHttpError40X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 40X".format(exception))



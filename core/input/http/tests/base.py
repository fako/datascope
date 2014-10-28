import json

from django.test import TestCase
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from mock import Mock

from core.input.http.base import HttpLink #, HttpQueryLink
from core.exceptions import HIFHttpError40X, HIFHttpError50X, HIFImproperUsage


class TestHttpLink(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):

        def test_callable():
            return "test"

        self.test_response = {
            "response_from_test": "test"
        }
        self.parameters = {
            "test-static": "test",
            "test-callable": test_callable
        }
        self.init_dict = {
            "head": '{"test-header":"test-header-content"}',
            "body": json.dumps(self.test_response),
            "status": 0,
            "retained": False,
            "type": "HttpLink",
            "identity": "test identity",
        }
        self.methods_get_uses = ['setup','send_request','handle_error', "store_response"]
        self.test_url = "http://localhost:8000/test/"

    def setup_mock_methods(self, http_link):
        for method in self.methods_get_uses:
            if method in ["load"]: continue
            setattr(http_link,method,Mock(return_value=True))
        return http_link

    def check_method_usage(self, http_link, methods_not_to_call):
        for method in self.methods_get_uses:
            if method in ["load"]: continue
            mock_method = getattr(http_link, method)
            if method in methods_not_to_call and not method == "setup":
                self.assertFalse(mock_method.called,"{} method shouldn't have been called".format(method))
            else:
                self.assertTrue(mock_method.called,"{} method should have been called".format(method))

    def test_init(self):
        http_link = HttpLink()
        self.assertEqual(http_link.refresh, False)
        self.assertEqual(http_link.session, None)
        self.assertEqual(http_link._link, '')

    def test_success_property(self):
        http_link = HttpLink()
        success_range = range(200, 300)
        for status in range(0,999):
            http_link.status = status
            if status in success_range:
                self.assertTrue(http_link.success, "Success property is not True with status={}".format(status))
            else:
                self.assertFalse(http_link.success, "Success property is not False with status={}".format(status))

    def test_url_property(self):
        # Setup the mock methods
        localhost = "http://localhost:8000/"
        misc_params = 'misc=1'
        auth_params = 'auth=1'
        http_link = HttpLink()
        http_link.prepare_link = Mock(return_value=localhost)
        http_link.prepare_params = Mock(return_value=misc_params)
        http_link.enable_auth = Mock(return_value=auth_params)
        # Test setting the URL property manually (not recommended)
        http_link.url = localhost
        self.assertEqual(http_link._link, localhost)
        # Test cached return
        self.assertEqual(http_link.url, localhost)
        self.assertFalse(http_link.prepare_link.called)
        self.assertFalse(http_link.prepare_params.called)
        self.assertFalse(http_link.enable_auth.called)
        # Try url generation
        http_link._link = None
        url = http_link.url
        self.assertIn(localhost, url)
        self.assertIn(misc_params, url)
        self.assertIn(auth_params, url)
        self.assertIn('?', url)
        self.assertIn('&', url)
        try:
            URLValidator(url)
        except ValidationError:
            self.fail("{} is not a valid URL".format(url))
        # Check whether correct methods got called
        self.assertTrue(http_link.prepare_link.called)
        self.assertTrue(http_link.prepare_params.called)
        self.assertTrue(http_link.enable_auth.called)
        # Adjust mocks to have no prepare_params
        http_link.url = None
        http_link.prepare_params = Mock(return_value='')
        http_link.enable_auth = Mock(return_value=auth_params)
        url = http_link.url
        self.assertIn(localhost, url)
        self.assertNotIn(misc_params, url)
        self.assertIn(auth_params, url)
        self.assertNotIn('&', url)
        try:
            URLValidator(url)
        except ValidationError:
            self.fail("{} is not a valid URL".format(url))
        # Adjust mocks not the have auth_params
        http_link.url = None
        http_link.prepare_params = Mock(return_value=misc_params)
        http_link.enable_auth = Mock(return_value='')
        url = http_link.url
        self.assertIn(localhost, url)
        self.assertIn(misc_params, url)
        self.assertNotIn(auth_params, url)
        self.assertNotIn('&', url)
        try:
            URLValidator(url)
        except ValidationError:
            self.fail("{} is not a valid URL".format(url))
        # Adjust mocks to have no params at all
        http_link.url = None
        http_link.prepare_params = Mock(return_value='')
        http_link.enable_auth = Mock(return_value='')
        url = http_link.url
        self.assertIn(localhost, url)
        self.assertNotIn(misc_params, url)
        self.assertNotIn(auth_params, url)
        self.assertNotIn('?', url)
        try:
            URLValidator(url)
        except ValidationError:
            self.fail("{} is not a valid URL".format(url))

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

        # Make call and test
        link = http_link.get()
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link, methods_not_to_call)

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
        http_link.status = 200

        # Make call and test
        http_link.refresh = True
        link = http_link.get()
        self.assertIsInstance(link, HttpLink)
        self.check_method_usage(http_link, methods_not_to_call)

    def test_prepare_link_method(self):
        http_link = HttpLink()
        localhost = u'http://localhost:8000'
        http_link.HIF_link = localhost
        link = http_link.prepare_link()
        self.assertIsInstance(link, unicode)
        self.assertEqual(link, localhost)

    def test_prepare_params_method(self):
        """
        Tests whether method returns the correct and valid GET params.
        """
        http_link = HttpLink(**self.init_dict)
        http_link.HIF_link = self.test_url
        http_link.HIF_parameters = self.parameters
        params = http_link.prepare_params()
        self.assertIsInstance(params, unicode)
        self.assertIn("test-static=test", params)
        self.assertIn("test-callable=test", params)

    def test_enable_auth_method(self):
        """
        Enable auth should return at least an empty unicode
        In subclasses it will do link specific authorization
        """
        http_link = HttpLink(**self.init_dict)
        http_link._link = self.test_url
        params = http_link.enable_auth()
        self.assertIsInstance(params, unicode)

    def test_store_response_function(self):
        http_link = HttpLink(**self.init_dict)
        http_link.save = Mock(return_value=True)
        # Test success
        http_link.status = 200
        http_link.store_response()
        self.assertFalse(http_link.store_response())
        self.assertFalse(http_link.save.called)
        # Test any non-success
        http_link.save.reset_mock()
        http_link.status = 500
        http_link.store_response()
        self.assertTrue(http_link.store_response())
        self.assertTrue(http_link.save.called)

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


# TODO: this changed to HttpQueryMixin, adjust tests accordingly
# class TestHttpQueryLink(TestCase):
#
#     def test_get(self):
#         # Setup vars
#         http_link = HttpQueryLink()
#         http_link.HIF_query_parameter = 'test'
#         http_link.status = 200  # prevents fetching data
#         # Test if argument ends up in parameters
#         http_link.get("test")
#         self.assertIn("test=test", http_link.url)
#         # Test giving no arguments
#         try:
#             http_link.get()
#             self.fail()
#         except HIFImproperUsage as exception:
#             self.assertEqual(str(exception), "QueryLinks should receive one input through args parameter it received 0.")
#         # Test giving too much arguments
#         try:
#             http_link.get("test", "wont-work")
#             self.fail()
#         except HIFImproperUsage as exception:
#             self.assertEqual(str(exception), "QueryLinks should receive one input through args parameter it received 2.")

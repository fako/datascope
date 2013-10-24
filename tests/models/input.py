import json

from mock import Mock

from django.test import TestCase
from HIF.models.input import DataLink
from HIF.exceptions import DbResponse


class TestDataLink(TestCase):
    fixtures = ['test-input.json']

    @classmethod
    def setUpClass(cls):
        cls.test_response = {
            "response_from_test": "test"
        }
        cls.translations = {
            "response_from_test": "response_translated"
        }
        cls.init_dict = {
            "response": json.dumps(cls.test_response),
            "hibernation": False,
            "link": "http://localhost:8000/test/",
            "link_type": "DataLink"
        }
        cls.methods_get_uses = ['prepare_link','enable_auth','send_request','handle_error',
        "continue_request","store_response","extract_results","translate_results","cleaner"]

    def setup_mock_methods(self, data_link):
        for method in self.methods_get_uses:
            if method in ["extract_results","translate_results"]:
                return_value = self.test_response
            else:
                return_value = True
            setattr(data_link,method,Mock(return_value=return_value))
        return data_link

    def check_method_usage(self, data_link, methods_not_to_call):
        for method in self.methods_get_uses:
            mock_method = getattr(data_link,method)
            if method in methods_not_to_call:
                self.assertFalse(mock_method.called)
            else:
                self.assertTrue(mock_method.called)

    def test_get_method_normal_execution(self):
        """
        This test tests the call of get
        It should call many other methods
        """
        # Test vars
        methods_not_to_call = []

        # Setup class
        data_link = DataLink(**self.init_dict)
        data_link = self.setup_mock_methods(data_link)

        # Make call and test
        result = data_link.get()
        self.assertIsInstance(result, list)
        self.check_method_usage(data_link,methods_not_to_call)


    def test_get_method_second_execution(self):
        """
        Test get again
        This time it should return cached results without calling functions.
        """
        # Test vars
        methods_not_to_call = self.methods_get_uses

        # Setup class
        data_link = DataLink(**self.init_dict)
        data_link = self.setup_mock_methods(data_link)
        data_link.results = [self.test_response]

        # Call and test
        result = data_link.get()
        self.assertIsInstance(result, list)
        self.check_method_usage(data_link, methods_not_to_call)

    def test_get_method_second_execution_refresh(self):
        """
        This test tests the call of get second time with refresh=True
        It should call many other methods
        """
        # Test vars
        methods_not_to_call = []

        # Setup class
        data_link = DataLink(**self.init_dict)
        data_link = self.setup_mock_methods(data_link)
        data_link.results = [self.test_response]


        # Make call and test
        result = data_link.get(refresh=True)
        self.assertIsInstance(result, list)
        self.check_method_usage(data_link, methods_not_to_call)

    def test_get_method_db_result(self):
        """
        This test tests the call of get
        It checks whether methods that could get skipped after db result get skipped
        """
        # Test vars
        methods_not_to_call = ["handle_error","continue_request","store_response"]

        # Mock functions
        def raise_db_response():
            raise DbResponse

        # Setup class
        data_link = DataLink(**self.init_dict)
        data_link = self.setup_mock_methods(data_link)
        data_link.send_request.side_effect = raise_db_response

        result = data_link.get()
        self.assertIsInstance(result, list)
        self.check_method_usage(data_link,methods_not_to_call)

    def test_enable_auth_method(self):
        """
        Enable auth should set the link that send_request will use.
        """
        data_link = DataLink(**self.init_dict)
        data_link.enable_auth()
        self.assertEqual(data_link.link, data_link.auth_link)

    def test_send_request_method_without_db_response(self):
        data_link = DataLink(**self.init_dict)
        try:
            data_link.send_request()
        except DbResponse:
            self.fail()
        self.assertFalse(data_link.hibernation)

    def test_send_request_method_with_dbresponse(self):
        data_link = DataLink(**self.init_dict)
        data_link.auth_link = "http://localhost:8000/test-db/"
        try:
            data_link.send_request()
            self.fail()
        except DbResponse:
            pass
        self.assertTrue(data_link.hibernation)

    def test_store_response_function(self):
        data_link = DataLink(**self.init_dict)
        data_link.cache = False
        self.assertFalse(data_link.store_response())
        data_link.cache = True
        self.assertTrue(data_link.store_response())
        data_link.response = ''
        self.assertFalse(data_link.store_response())

    def test_translate_results_function(self):
        data_link = DataLink(**self.init_dict)
        data_link.results = [self.test_response]
        data_link._translations = self.translations
        data_link.translate_results()
        self.assertIn("response_translated",data_link.results[0])

    def test_hibernate_function(self):
        data_link = DataLink(**self.init_dict)
        self.assertFalse(data_link.hibernate())
        data_link.results = [self.test_response]
        self.assertTrue(data_link.hibernate())
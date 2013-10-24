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
        cls.init_dict = {
            "response": json.dumps(cls.test_response),
            "hibernation": False,
            "link": "http://localhost:8000/test/",
            "link_type": "DataLink"
        }
        cls.methods_get_uses = ['prepare_link','enable_auth','send_request','handle_error',
        "continue_request","store_response","extract_results","translate_results"]

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
        for method in self.methods_get_uses:
            setattr(data_link,method,Mock(return_value=True))

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
        data_link.results.append(data_link.response)
        for method in self.methods_get_uses:
            setattr(data_link,method,Mock(return_value=True))

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
        data_link.results.append(data_link.response)
        for method in self.methods_get_uses:
            setattr(data_link,method,Mock(return_value=True))

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
        for method in self.methods_get_uses:
            setattr(data_link,method,Mock(return_value=True))
        data_link.send_request.side_effect = raise_db_response

        result = data_link.get()
        self.assertIsInstance(result, list)
        self.check_method_usage(data_link,methods_not_to_call)

    def test_cleaner_present(self):
        """
        The cleaner is hard to test using get method tests.
        So we check for it explicitly.
        """
        data_link = DataLink(**self.init_dict)
        self.assertTrue(hasattr(data_link,"cleaner"))
        self.assertTrue(hasattr(data_link.cleaner,"__call__"))

    def test_enable_auth_function(self):
        """
        Enable auth should set the link that send_request will use.
        """
        data_link = DataLink(**self.init_dict)
        data_link.enable_auth()
        self.assertEqual(data_link.link, data_link.auth_link)

    def test_send_request_function_with_dbresponse(self):
        pass

    def test_send_request_function_without_db_response(self):
        pass

    def test_store_response_function(self):
        pass

    def test_translate_results_function(self):
        pass

    def test_hibernate_function(self):
        pass
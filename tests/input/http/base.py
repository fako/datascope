import json

from django.test import TestCase
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from HIF.input.http.base import HTTPLink

class TestHTTPLink(TestCase):

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
            "response": json.dumps(cls.test_response),
            "response_status": 200,
            "hibernation": False,
            "link": "http://localhost:8000/test/",
            "link_type": "DataLink"
        }

    def test_prepare_link_method(self):
        """
        Tests whether the link is appended with parameters
        And is valid
        """
        http_link = HTTPLink(**self.init_dict)
        http_link._parameters = self.parameters
        http_link._link = http_link.link # little hack
        http_link.prepare_link()
        self.assertIn("?",http_link.link)
        self.assertIn("test-static=test",http_link.link)
        self.assertIn("test-callable=test",http_link.link)
        try:
            validator = URLValidator()
            validator(http_link.link)
        except ValidationError:
            self.fail("{} by prepare_link did not validate.".format(http_link.link))

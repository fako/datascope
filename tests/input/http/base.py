import json

from django.test import TestCase
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from HIF.input.http.base import HTTPLink
from HIF.exceptions import HIFHTTPError40X, HIFHTTPError50X

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

    def test_handle_error_method(self):
        statuses_50X = range(500,505)
        statuses_40X = range(400,410)
        http_link = HTTPLink(**self.init_dict)
        for status in statuses_50X:
            http_link.response_status = status
            try:
                http_link.handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except HIFHTTPError50X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception {} expecting 50X".format(exception))
        for status in statuses_40X:
            http_link.response_status = status
            try:
                http_link.handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except HIFHTTPError40X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception {} expecting 40X".format(exception))



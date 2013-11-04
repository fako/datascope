from django.test import TestCase

from HIF.input.http.links import HttpLink, HttpQueryLink
from HIF.exceptions import HIFCouldNotLoadFromStorage


class TestHttpStorage(TestCase):
    fixtures = ['test-storage']

    @classmethod
    def setUpClass(cls):
        cls.init_dict = {
            "identifier": "http://localhost:8000/test/",
            "type": "HttpLink"
        }

    def test_http_load(self):
        link = HttpLink(**self.init_dict)
        link.load()
        self.assertEqual(link.body,"Test body")
        self.assertEqual(link.head,"Test head")
        self.assertEqual(link.type,"HttpLink")
        link.load("http://localhost:8000/test/test/")
        self.assertEqual(link.body,"Test another body")
        self.assertEqual(link.head,"Test another head")
        self.assertEqual(link.type,"HttpLink")

    def test_http_query_load(self):
        init = dict(self.init_dict)
        link = HttpQueryLink({"query": "HIF"}, **init)
        link.load()
        self.assertEqual(link.body,"Test query body")
        self.assertEqual(link.head,"Test query head")
        self.assertEqual(link.type,"HttpQueryLink")

    def test_http_no_results(self):
        init = dict(self.init_dict)
        link = HttpQueryLink({"query": "HIF"}, **init)
        link.identifier = "http://localhost:8000/test/test/"
        try:
            link.load()
            self.fail()
        except HIFCouldNotLoadFromStorage as exception:
            self.assertEqual(str(exception), "Model with identifier={} and type={} does not exist".format(link.identifier,link.__class__.__name__))

    def test_bad_identifier(self):
        link = HttpLink(**self.init_dict)
        link.identifier = None
        try:
            link.load()
            self.fail()
        except HIFCouldNotLoadFromStorage as exception:
            self.assertEqual(str(exception), "No storage identifier set or given")

    def test_http_retain(self):
        link = HttpLink(**self.init_dict)
        link.load()
        self.assertEqual(link.retained, None)
        link.retain()
        self.assertTrue(link.retained)
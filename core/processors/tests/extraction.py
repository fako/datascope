from __future__ import unicode_literals, absolute_import, print_function, division

from bs4 import BeautifulSoup
from mock import Mock

from django.test import TestCase

from core.processors.extraction import ExtractProcessor
from core.tests.mocks.data import MOCK_HTML, MOCK_SCRAPE_DATA, MOCK_DATA_WITH_RECORDS, MOCK_JSON_DATA


class TestExtractProcessorHTML(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.content_types = ["text/html", "application/json", "nothing/quantum"]
        self.html_obj = {
            "@": "soup.find_all('a')",
            "text": "el.text",
            "link": "el['href']",
            "#page": "soup.find('title').text",
        }
        self.html_prc = ExtractProcessor(config={"objective": self.html_obj})
        self.soup = BeautifulSoup(MOCK_HTML)
        self.json_obj = {
            "@": "$.records",
            "#unicode": "$.unicode.0",
            "#goal": "$.dict.dict.test",
            "id": "$.id",
            "record": "$.record"
        }
        self.json_prc = ExtractProcessor(config={"objective": self.json_obj})
        self.json = MOCK_DATA_WITH_RECORDS

    def test_init_and_load_objective(self):
        self.assertEqual(self.html_prc._at, "soup.find_all('a')")
        self.assertEqual(self.html_prc._context, {"page": "soup.find('title').text"})
        self.assertEqual(self.html_prc._objective, {"text": "el.text", "link": "el['href']"})

    def test_extract(self):
        self.html_prc.text_html = Mock()
        self.html_prc.application_json = Mock()
        for content_type in self.content_types:
            try:
                self.html_prc.extract(content_type, {"test": "test"})
            except TypeError:
                self.assertEqual(
                    content_type,
                    "nothing/quantum", "{} does not exist as a method on ExtractProcessor.".format(content_type)
                )
        self.assertTrue(self.html_prc.text_html.called)
        self.assertTrue(self.html_prc.application_json.called)

    def test_html_text(self):
        rsl = self.html_prc.text_html(self.soup)
        self.assertEqual(rsl, MOCK_SCRAPE_DATA)
        self.assertIsInstance(rsl, list, "Extractors are expected to return lists with 0 or more elements inside.")

    def test_application_json(self):
        rsl = self.json_prc.application_json(self.json)
        self.assertEqual(rsl, MOCK_JSON_DATA)
        self.assertIsInstance(rsl, list, "Extractors are expected to return lists with 0 or more elements inside.")

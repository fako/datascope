from __future__ import unicode_literals, absolute_import, print_function, division

from copy import copy

from bs4 import BeautifulSoup
from mock import Mock

from django.test import TestCase

from core.processors.extraction import ExtractProcessor
from core.tests.mocks import MOCK_HTML, MOCK_SCRAPE_DATA


class TestExtractProcessorHTML(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.content_types = ["text/html", "application/json", "nothing/quantum"]
        self.objective = {
            "@": "soup.find_all('a')",
            "text": "el.text",
            "link": "el['href']",
            "#page": "soup.find('title').text",
        }
        self.prc = ExtractProcessor(objective=self.objective)
        self.soup = BeautifulSoup(MOCK_HTML)

    def test_init_and_load_objective(self):
        self.assertEqual(self.prc._at, "soup.find_all('a')")
        self.assertEqual(self.prc._context, {"page": "soup.find('title').text"})
        self.assertEqual(self.prc._objective, {"text": "el.text", "link": "el['href']"})

    def test_extract(self):
        self.prc.text_html = Mock()
        self.prc.application_json = Mock()
        for content_type in self.content_types:
            try:
                self.prc.extract(content_type, {"test": "test"})
            except TypeError:
                self.assertEqual(
                    content_type,
                    "nothing/quantum", "{} does not exist as a method on ExtractProcessor.".format(content_type)
                )
        self.assertTrue(self.prc.text_html.called)
        self.assertTrue(self.prc.application_json.called)

    def test_html_text(self):
        rsl = self.prc.text_html(self.soup)
        self.assertEqual(rsl, MOCK_SCRAPE_DATA)
        self.assertIsInstance(rsl, list, "Extractors are expected to return lists with 0 or more elements inside.")

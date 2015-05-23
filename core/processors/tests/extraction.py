from bs4 import BeautifulSoup

from django.test import TestCase

from core.processors.extraction import ExtractProcessor
from core.tests.mocks import MOCK_HTML, MOCK_SCRAPE_DATA


class TestExtractProcessorHTML(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.prc = ExtractProcessor(objective={
            "@": "soup.find_all('a')",
            "text": "el.text",
            "link": "el['href']",
            "#page": "soup.find('title').text",
        })
        self.soup = BeautifulSoup(MOCK_HTML)

    def test_init(self):
        self.fail("test")

    def test_load_objective(self):
        self.fail("test")

    def test_extract(self):
        self.fail("test")

    def test_html_text(self):
        rsl = self.prc.text_html(self.soup)
        self.assertEqual(rsl, MOCK_SCRAPE_DATA)

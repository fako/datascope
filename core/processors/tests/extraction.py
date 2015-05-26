from bs4 import BeautifulSoup

from django.test import TestCase

from mock import Mock

from core.processors.extraction import ExtractProcessor
from core.tests.mocks import MOCK_HTML, MOCK_SCRAPE_DATA


class TestExtractProcessorHTML(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.objective = {
            "@": "soup.find_all('a')",
            "text": "el.text",
            "link": "el['href']",
            "#page": "soup.find('title').text",
        }
        self.prc = ExtractProcessor(objective=self.objective)
        self.soup = BeautifulSoup(MOCK_HTML)

    def test_init(self):
        ExtPrc = ExtractProcessor
        ExtPrc.load_objective = Mock()
        ExtPrc(objective=self.objective)
        self.assertTrue(ExtPrc.load_objective.called)

    def test_load_objective(self):
        self.fail("test")

    def test_extract(self):
        self.fail("test")

    def test_html_text(self):
        rsl = self.prc.text_html(self.soup)
        self.assertEqual(rsl, MOCK_SCRAPE_DATA)
        self.assertIsInstance(rsl, list, "Extractors are expected to return lists with 0 or more elements inside.")

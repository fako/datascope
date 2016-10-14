from __future__ import unicode_literals, absolute_import, print_function, division

from bs4 import BeautifulSoup
from mock import Mock
from types import GeneratorType

from django.test import TestCase

from core.processors.extraction import ExtractProcessor
from core.tests.mocks.data import (MOCK_HTML, MOCK_SCRAPE_DATA, MOCK_DATA_WITH_RECORDS, MOCK_JSON_DATA,
                                   MOCK_DATA_WITH_KEYS)


class TestExtractProcessor(TestCase):

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
        self.soup = BeautifulSoup(MOCK_HTML, "html.parser")
        self.json_obj = {
            "@": "$.records",
            "#unicode": "$.unicode.0",
            "#goal": "$.dict.dict.test",
            "id": "$.id",
            "record": "$.record"
        }
        self.json_prc = ExtractProcessor(config={"objective": self.json_obj})
        self.json_records = MOCK_DATA_WITH_RECORDS
        self.json_dict = MOCK_DATA_WITH_KEYS

        self.test_resources_data = [self.soup, self.json_records, None]
        self.test_resources_extractions = [MOCK_SCRAPE_DATA, MOCK_JSON_DATA, None]
        self.test_resources = [
            (Mock(content=(content_type, data)), processor,)
            for content_type, data, processor in zip(
                self.content_types,
                self.test_resources_data,
                [self.html_prc, self.json_prc, self.html_prc]
            )
        ]

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

    def test_extract_from_resource(self):
        data = []
        try:
            for test_resource in self.test_resources:
                resource, processor = test_resource
                data.append(processor.extract_from_resource(resource))
            self.fail("Wrong content_type did not raise exception")
        except TypeError:
            pass
        for test_result, expected_data in zip(data, self.test_resources_extractions):
            self.assertIsInstance(test_result, GeneratorType)
            self.assertEqual(list(test_result), expected_data)

    def test_pass_resource_through(self):
        for test_resource, expected_data in zip(self.test_resources, self.test_resources_data):
            resource, processor = test_resource
            data = processor.pass_resource_through(resource)
            self.assertNotIsInstance(data, GeneratorType)
            self.assertIs(data, expected_data)

    def test_html_text(self):
        rsl = self.html_prc.text_html(self.soup)
        self.assertEqual(list(rsl), MOCK_SCRAPE_DATA)
        self.assertIsInstance(rsl, GeneratorType, "Extractors are expected to return generators.")

    def test_application_json_records(self):
        rsl = self.json_prc.application_json(self.json_records)
        self.assertEqual(list(rsl), MOCK_JSON_DATA)
        self.assertIsInstance(rsl, GeneratorType, "Extractors are expected to return generators.")

    def test_application_json_dict(self):
        self.json_obj["@"] = "$.keys"
        keys_processor = ExtractProcessor(config={"objective": self.json_obj})
        rsl = keys_processor.application_json(self.json_dict)
        self.assertEqual(list(rsl), MOCK_JSON_DATA)
        self.assertIsInstance(rsl, GeneratorType, "Extractors are expected to return generators.")

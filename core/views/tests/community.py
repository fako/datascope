from copy import copy
from mock import patch, MagicMock

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.test import Client
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse

from rest_framework.response import Response

from core.models.resources.manifestation import Manifestation
from core.views import CommunityView, HtmlCommunityView
from core.tests.mocks.community import CommunityMock
from core.exceptions import DSProcessUnfinished, DSProcessError


class TestCommunityView(TestCase):

    fixtures = ["test-community"]

    def setUp(self):
        self.view = CommunityView()

    def check_response(self, response, status_code):
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status_code)

    def check_manifestations(self, count):
        self.assertEqual(Manifestation.objects.count(), count)

    def test_get_full_path(self):
        full_path = CommunityView.get_full_path(CommunityMock, "test/path", {"test": "test"})
        self.assertEqual(full_path, "/data/v1/mock/service/test/path?test=test")

    @patch("core.models.organisms.community.Community.grow", side_effect=ValidationError("Invalid"))
    def test_get_response_invalid(self, grow_patch):
        response = self.view.get_response(CommunityMock, "test", {"setting1": "const"})
        self.check_response(response, 400)
        self.check_manifestations(0)

    @patch("core.models.organisms.community.Community.grow", side_effect=DSProcessUnfinished())
    def test_get_response_accepted(self, grow_patch):
        response = self.view.get_response(CommunityMock, "test", {"setting1": "const"})
        self.check_response(response, 202)
        self.check_manifestations(0)
        response = self.view.get_response(CommunityMock, "test-synchronous", {})
        self.check_response(response, 202)
        self.check_manifestations(0)

    @patch("core.models.organisms.community.Community.grow", side_effect=DSProcessError())
    def test_get_response_error(self, grow_patch):
        response = self.view.get_response(CommunityMock, "test", {"setting1": "const"})
        self.check_response(response, 500)
        self.check_manifestations(0)

    @patch("core.models.organisms.community.Community.grow")
    def test_get_empty_response(self, grow_patch):
        response = self.view.get_response(CommunityMock, "test-empty", {"setting1": "const"})
        self.check_response(response, 204)
        self.check_manifestations(1)

    @patch("core.models.organisms.community.Community.grow")
    def test_get_response_ok(self, grow_patch):
        response = self.view.get_response(CommunityMock, "test-ready", {"setting1": "const"})
        self.check_response(response, 200)
        self.check_manifestations(1)
        response = self.view.get_response(CommunityMock, "test-ready", {"setting1": "const"})
        self.check_response(response, 200)
        self.check_manifestations(1)
        grow_patch.assert_called_once()

    def test_get(self):
        client = Client()
        response = client.get("/data/v1/mock/service/test-ready/?setting1=const")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "error": None,
            "status": {},
            "result": {},
            "actions": [],
            "results": [
                {
                    "context": "nested value",
                    "value": "nested value 0",
                    "number": 1
                },
                {
                    "context": "nested value",
                    "value": "nested value 1",
                    "number": 2
                },
                {
                    "context": "nested value",
                    "value": "nested value 2",
                    "number": 3
                }
            ]
        })

    def test_get_invalid_time(self):
        client = Client()
        response = client.get("/data/v1/mock/service/test-ready/?setting1=const&t=1")
        self.assertEqual(response.status_code, 404)

    def test_get_valid_time(self):
        client = Client()
        response = client.get("/data/v1/mock/service/test-ready/?setting1=const&t=20160605161754000")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "error": None,
            "status": {},
            "result": {},
            "actions": [],
            "results": [
                {
                    "context": "nested value",
                    "value": "nested value 0",
                    "number": 1
                },
                {
                    "context": "nested value",
                    "value": "nested value 2",
                    "number": 3
                }
            ]
        })


class TestHtmlCommunityView(TestCase):

    fixtures = ["test-community"]

    def setUp(self):
        self.client = Client()
        self.ready_url = "/data/v1/mock/html/test-ready/?setting1=const"
        self.processing_url = "/data/v1/mock/html/test/?setting1=const"
        self.index_url = "/data/v1/mock/html/?setting1=const"
        self.empty_url = "/data/v1/mock/html/test-empty/?setting1=const"

    def check_response(self, response, template, data):
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "mock/" + template)
        self.assertEqual(response.context_data, {
            "self_reverse": "mock_html",
            "response": data
        })

    def get_empty_data(self):
        return copy(CommunityView.RESPONSE_DATA)

    def test_html_template_for(self):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/ok.html")
        mock_response.status_code = 202
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/accepted.html")
        mock_response.status_code = 204
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/no-content.html")
        mock_response.status_code = 404
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/no-content.html")
        mock_response.status_code = 400
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/bad-request.html")
        mock_response.status_code = 500  # or any other status
        template = HtmlCommunityView.html_template_for(CommunityMock, mock_response)
        self.assertEqual(template, "mock/index.html")

    def test_data_for(self):
        mock_data = {"test": "test"}
        mock_response = MagicMock(spec=Response)
        mock_response.data = mock_data
        mock_response.status_code = 200
        data = HtmlCommunityView.data_for(CommunityMock, mock_response)
        self.assertEqual(data, mock_data)
        mock_response.status_code = 300
        data = HtmlCommunityView.data_for(CommunityMock, mock_response)
        self.assertEqual(data, mock_data)
        mock_response.status_code = 500  # or any other status
        data = HtmlCommunityView.data_for(CommunityMock, mock_response)
        self.assertIsNone(data)
        data = HtmlCommunityView.data_for(CommunityMock, None)
        self.assertIsNone(data)

    @patch("core.models.organisms.community.Community.grow", side_effect=ValidationError("Invalid"))
    def test_get_response_invalid(self, grow_patch):
        response = self.client.get(self.processing_url)
        context_data = self.get_empty_data()
        context_data["error"] = "Invalid"
        self.check_response(response, "bad-request.html", context_data)
        self.assertContains(response, "<p>Invalid</p>")

    @patch("core.models.organisms.community.Community.grow", side_effect=DSProcessUnfinished())
    def test_get_response_accepted(self, grow_patch):
        response = self.client.get(self.processing_url)
        self.check_response(response, "accepted.html", None)
        self.assertContains(response, '<p id="wait-text">')

    @patch("core.models.organisms.community.Community.grow", side_effect=DSProcessError())
    def test_get_response_error(self, grow_patch):  # TODO: do not ignore errors
        response = self.client.get(self.processing_url)
        self.check_response(response, "index.html", None)

    @patch("core.models.organisms.community.Community.grow", side_effect=DSProcessUnfinished())
    def test_index_response(self, grow_patch):
        response = self.client.get(self.index_url)
        self.check_response(response, "index.html", None)
        self.assertContains(response, "<p>Search for something fake.</p>")
        grow_patch.assert_not_called()
        CommunityMock.INPUT_THROUGH_PATH = False
        response = self.client.get(self.index_url)
        self.check_response(response, "accepted.html", None)
        self.assertContains(response, '<p id="wait-text">')
        grow_patch.assert_called_once()
        CommunityMock.INPUT_THROUGH_PATH = True

    @patch("core.models.organisms.community.Community.grow")
    def test_get_response_ok(self, grow_patch):
        response = self.client.get(self.ready_url)
        self.check_response(response, "ok.html", {
            "error": None,
            "status": {},
            "result": {},
            "actions": [],
            "results": [
                {
                    "context": "nested value",
                    "value": "nested value 0",
                    "number": 1
                },
                {
                    "context": "nested value",
                    "value": "nested value 1",
                    "number": 2
                },
                {
                    "context": "nested value",
                    "value": "nested value 2",
                    "number": 3
                }
            ]
        })
        self.assertContains(response, "<p>nested value 0</p>")
        self.assertContains(response, "<p>nested value 1</p>")
        self.assertContains(response, "<p>nested value 2</p>")

    def test_get_response_empty(self):
        response = self.client.get(self.empty_url)
        self.check_response(response, "no-content.html", None)
        self.assertContains(response, "<p>No results found, please try again.</p>")

    def test_get_invalid_time(self):
        response = self.client.get(self.ready_url + "&t=1")
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_get_valid_time(self):
        response = self.client.get(self.ready_url + "&t=20160605161754000")
        self.assertEqual(response.status_code, 200)
        self.check_response(response, "ok.html", {
            "error": None,
            "status": {},
            "result": {},
            "actions": [],
            "results": [
                {
                    "context": "nested value",
                    "value": "nested value 0",
                    "number": 1
                },
                {
                    "context": "nested value",
                    "value": "nested value 2",
                    "number": 3
                }
            ]
        })
        self.assertContains(response, "<p>nested value 0</p>")
        self.assertNotContains(response, "<p>nested value 1</p>")
        self.assertContains(response, "<p>nested value 2</p>")

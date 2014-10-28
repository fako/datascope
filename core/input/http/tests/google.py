import integration  # do not import TestCase classes directly, or they will get tested!

from django.test import TestCase

from core.input.http.google import GoogleLink, GoogleImage
from core.exceptions import HIFHttpError40X, HIFHttpLinkPending


class TestGoogleLink(TestCase):

    def setUp(self):
        self.instance = GoogleLink()
        self.instance.setup()

    def test_google_link_handle_error(self):
        for status in range(400,500):
            self.instance.status = status
            try:
                self.instance.handle_error()
                self.fail("GoogleLink.handle_error() did not raise exception when status in 400-500 range")
            except HIFHttpError40X:
                self.assertNotEqual(self.instance.status, 403, "GoogleLink.handle_error() raised a 40X with status 403")
            except HIFHttpLinkPending:
                self.assertEqual(self.instance.status, 403, "GoogleLink.handle_error() raised a LinkPending with status other than 403")

    def test_google_image_enable_auth(self):
        params = self.instance.enable_auth()
        self.assertIn("key=", params)


class TestGoogleImage(integration.TestExternalResourceIntegration):

    HIF_model = GoogleImage

    def test_google_image_enable_auth(self):
        params = self.instance.enable_auth()
        self.assertIn("cx=", params)

import integration  # do not import TestCase classes directly, or they will get tested!

from HIF.input.http.google import GoogleImage


class TestGoogleImage(integration.TestExternalResourceIntegration):

    HIF_model = GoogleImage
import unittest

from django.test import TestCase


class TestExternalResourceIntegration(TestCase):
    """
    Class should look into Domain() to see whether integration testing is wanted
    The test looks at most often over ridden methods and checks input

    Perhaps we need to sublass for Query and JsonQuery
    """

    HIF_model = ""

    @unittest.skip("a skipping test")
    def test_integration_get_model(self):
        # Use get_hif_model to see whether it really exists
        pass

    def test_integration_prepare_link(self):
        # Should return valid URL in unicode!
        pass

    def test_integration_prepare_params(self):
        # Should return valid params string or empty string
        # Should return string
        # Look at HIF_parameters
        # Return unicode!
        pass

    def test_integration_enable_auth(self):
        # Should return valid params string or empty string
        # Should return string
        # Return unicode!
        pass

    def test_integration_get(self):
        # Should return at least one valid object
        pass


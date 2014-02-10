import unittest

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from HIF.models.settings import Domain
from HIF.models.tests.integrity import TestModelIntegrity


class TestExternalResourceIntegration(TestModelIntegrity):
    """
    The test looks at most often over ridden methods and checks input.
    It also uses get() and sees whether we get expected results.
    """

    # Helper methods to assist in testing

    @staticmethod
    def split_param_keys_and_values(params):
        keys = []
        values = []
        items = params.split('&')
        for item in items:
            key, value = item.split('=')
            keys.append(key)
            values.append(value)
        return keys, values

    def get_translated_objective(self):
        objective = dict(self.instance.HIF_objective)
        for key, value in self.instance.HIF_translations.iteritems():
            if key in objective:
                objective[value] = objective[key]
                del(objective[key])
        return objective

    # Checks that will get used by several tests or reused in different ways

    def check_response_validity(self):
        self.assertEqual(self.instance.status, 200)
        self.assertTrue(self.instance.body)
        self.assertTrue(self.instance.head)

    def check_data_validity(self):
        self.assertGreaterEqual(self.instance.data, 1)
        self.assertEqual(self.instance.data[0].keys(), self.get_translated_objective().keys())

    # Actual tests

    def test_integration_prepare_link(self):
        link = self.instance.prepare_link()
        self.assertIsInstance(link, unicode)
        try:
            URLValidator(link)
        except ValidationError:
            self.fail()

    def test_integration_prepare_params(self):
        # Most basic checks
        params = self.instance.prepare_params()
        self.assertIsInstance(params, unicode)
        # Additional checks if there are parameters
        if params:
            keys, values = self.split_param_keys_and_values(params)
            for key, value in self.instance.HIF_parameters.iteritems():
                if callable(value):
                    value = value()
                if key not in keys:
                    self.fail("Parameter key '{}' not found in prepare_params output".format(key))
                if value and unicode(value) not in values:
                    self.fail("Parameter value '{}' not found in prepare_params output".format(value))

    def test_integration_enable_auth(self):
        params = self.instance.prepare_params()
        self.assertIsInstance(params, unicode)

    @unittest.skipIf(Domain().TEST_skip_external_resource_integration, "because the Domain refuses integration tests")
    def test_integration_get(self):
        """
        The only type of get() we're testing here is the get() found on JsonQueryLinks.
        At some point in the future this function may have an if-else structure where it will run tests
        according to the type of object being tested
        """
        self.instance.get(Domain().TEST_query)
        self.check_response_validity()
        self.check_data_validity()


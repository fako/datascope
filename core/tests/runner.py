import logging

from django.test.runner import DiscoverRunner


class DataScopeDiscoverRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        logging.disable(logging.DEBUG)
        return super(DataScopeDiscoverRunner, self).run_tests(test_labels, extra_tests, **kwargs)
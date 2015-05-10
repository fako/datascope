from django.test import TestCase

from core.exceptions import DSHttpError50X, DSHttpError40X
from core.models.resources.http import HttpResourceMock


class HttpResourceTestMixin(TestCase):

    def setUp(self):
        super(HttpResourceTestMixin, self).setUp()
        self.instance = self.get_test_instance()

    @staticmethod
    def get_test_instance():
        raise NotImplementedError()

    def test_data(self):
        # type only
        pass

    def test_parameters(self):
        self.assertIsInstance(self.instance.parameters(), dict)

    def test_auth_parameters(self):
        self.assertIsInstance(self.instance.auth_parameters(), dict)

    def test_next_parameters(self):
        self.assertIsInstance(self.instance.next_parameters(), dict)

    def test_send_request(self):
        pass

    def test_success(self):
        success_range = range(200, 207)
        for status in range(0, 999):
            self.instance.status = status
            if status in success_range:
                self.assertTrue(self.instance.success, "Success property is not True with status={}".format(status))
            else:
                self.assertFalse(self.instance.success, "Success property is not False with status={}".format(status))

    def test_handle_error(self):
        statuses_50x = range(500, 505)
        statuses_40x = range(400, 410)
        for status in statuses_50x:
            self.instance.status = status
            try:
                self.instance._handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except DSHttpError50X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 50X".format(exception))
        for status in statuses_40x:
            self.instance.status = status
            try:
                self.instance._handle_error()
                self.fail("Handle error doesn't handle status {}".format(status))
            except DSHttpError40X:
                pass
            except Exception, exception:
                self.fail("Handle error throws wrong exception '{}' expecting 40X".format(exception))


class ConfigurationFieldTestMixin(TestCase):

    def setUp(self):
        super(ConfigurationFieldTestMixin, self).setUp()
        self.instance = self.get_test_instance()

    @staticmethod
    def get_test_instance():
        raise NotImplementedError()

    def test_set_storage_load_and_get(self):
        pass


class TestHttpResource(HttpResourceTestMixin, ConfigurationFieldTestMixin):

    @staticmethod
    def get_test_instance():
        return HttpResourceMock()

    def test_get(self):
        # init, new
        # init, load
        # init, load -> retry
        # preset, new
        # preset, load
        # preset, load -> retry
        pass

    def test_request_with_auth(self):
        pass

    def test_request_without_auth(self):
        pass

    def test_create_next_request(self):
        pass

    def test_validate_request(self):
        pass


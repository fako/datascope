from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.conf import settings

from datagrowth.resources import HttpResource


class BrowserResource(HttpResource):  # TODO: write tests

    def _send(self):
        # TODO: handle sessions that are set by the context
        # TODO: handle POST
        # TODO: handle set headers
        assert self.request and isinstance(self.request, dict), \
            "Trying to make request before having a valid request dictionary."

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        browser = webdriver.PhantomJS(
            desired_capabilities=dcap,
            service_args=['--ignore-ssl-errors=true'],
            service_log_path=settings.PATH_TO_LOGS + "ghostdriver.log"
        )

        url = self.request.get("url")
        browser.get(url)

        self._update_from_response(browser)

    def _update_from_response(self, response):
        self.head = dict()
        self.status = 1
        self.body = response.page_source
        self.soup = BeautifulSoup(self.body, "html5lib")

    @property
    def success(self):
        """
        This needs to be checked per resource based on the returned HTML. Status codes are not available:
        https://code.google.com/p/selenium/issues/detail?id=141

        :return: Boolean indicating success
        """
        return self.status == 1

    def transform(self, soup):
        """

        :return:
        """
        raise NotImplementedError()

    @property
    def content(self):
        """

        :return: content_type, data
        """
        if self.success:
            return "application/json", self.transform(self.soup)
        return None, None

    def __init__(self, *args, **kwargs):
        super(HttpResource, self).__init__(*args, **kwargs)
        self.soup = BeautifulSoup(self.body if self.body else "", "html5lib")

    class Meta:
        abstract = True


class URLResource(HttpResource):

    def _create_url(self, *args):
        return args[0]

    class Meta:
        abstract = True


class MicroServiceResource(HttpResource):

    CONFIG_NAMESPACE = "micro_service"

    MICRO_SERVICE = "mock_service"
    MICRO_SERVICE_PROTOCOL = "http"
    MICRO_SERVICE_PATH = "/service/"

    URI_TEMPLATE = "{}://{}{}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = self.config.connections[self.MICRO_SERVICE]

    def send(self, method, *args, **kwargs):
        args = (self.connection["protocol"], self.connection["host"], self.connection["path"]) + args
        return super().send(method, *args, **kwargs)

    class Meta:
        abstract = True

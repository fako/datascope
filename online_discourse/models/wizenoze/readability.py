from copy import copy

from core.models.resources.http import HttpResource


class ReadabilityClassification(HttpResource):

    URI_TEMPLATE = "https://api.wizenoze.com/v2/classify/url"

    HEADERS = {
        "Content-Type": "application/json"
    }

    CONFIG_NAMESPACE = "wizenoze"

    def headers(self):
        headers = copy(self.HEADERS)
        headers["Authorization"] = self.config.api_key
        return headers

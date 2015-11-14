from __future__ import unicode_literals, absolute_import, print_function, division

from copy import copy

from core.exceptions import DSInvalidResource
from sources.models.google.query import GoogleQuery


class GoogleImage(GoogleQuery):

    URI_TEMPLATE = 'https://www.googleapis.com/customsearch/v1?{}="{}"'
    PARAMETERS = {
        "searchType": "image",
        "cr": None  # set at runtime if present
    }

    def send(self, method, *args, **kwargs):
        if len(args) > 1:
            self.config.country = args[1]
            args = (args[0],)
        return super(GoogleImage, self).send(method, *args, **kwargs)

    def parameters(self):
        params = copy(self.PARAMETERS)
        params["cr"] = self.config.country
        return params

    def auth_parameters(self):
        params = super(GoogleImage, self).auth_parameters()
        params.update({
            "cx": self.config.cx
        })
        return params

    @property
    def content(self):
        content_type, data = super(GoogleImage, self).content
        try:
            data["queries"]["request"][0]["searchTerms"] = data["queries"]["request"][0]["searchTerms"][1:-1]
        except (KeyError, IndexError):
            raise DSInvalidResource("Google Image resource does not specify searchTerms", self)
        return content_type, data

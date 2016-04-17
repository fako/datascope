from __future__ import unicode_literals, absolute_import, print_function, division

from copy import copy

from core.exceptions import DSInvalidResource
from sources.models.google.query import GoogleQuery


class GoogleImage(GoogleQuery):

    URI_TEMPLATE = 'https://www.googleapis.com/customsearch/v1?q="{}"'
    PARAMETERS = {
        "searchType": "image",
        "cr": None  # set at runtime if present
    }
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",  # the query string
                },
                {
                    "type": "integer",  # amount of desired images
                },
                {
                    "type": "string",  # example: countryXX
                    "maxLength": 9,
                    "minLength": 9
                },
            ],
            "additionalItems": False,
            "minItems": 1
        },
        "kwargs": None
    }

    def variables(self, *args):
        args = args or self.request.args
        variables = {}
        variables["url"] = (args[0],)
        try:
            variables["quantity"] = args[1]
            variables["country"] = args[2]
        except IndexError:
            pass
        return variables

    def parameters(self, **kwargs):
        params = copy(self.PARAMETERS)
        params["cr"] = kwargs.get("country")
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

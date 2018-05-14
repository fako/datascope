from copy import copy

from core.exceptions import DSInvalidResource
from sources.models.google.query import GoogleQuery


class GoogleImage(GoogleQuery):

    URI_TEMPLATE = 'https://www.googleapis.com/customsearch/v1?q="{}"'
    PARAMETERS = {
        "searchType": "image",
        "cr": ""  # set at runtime if present
    }
    GET_SCHEMA = {
        "args": {
            "type": "array",
            "items": [
                {
                    "type": "string",  # the query string
                },
                {
                    "anyOf": [
                        {
                            "type": "string",  # example: countryXX
                            "maxLength": 9,
                            "minLength": 9
                        },
                        {
                            "type": "null"
                        }
                    ]
                },
                {
                    "type": "integer",  # amount of desired images
                },
            ],
            "additionalItems": False,
            "minItems": 1
        },
        "kwargs": None
    }

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "url": (args[0],),
            "country": args[1] if len(args) > 1 else None,
            "quantity": args[2] if len(args) > 2 else 0,
        }

    def parameters(self, **kwargs):
        params = copy(self.PARAMETERS)
        country = kwargs.get("country", "")
        if not country:
            del params["cr"]
        else:
            params["cr"] = country
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
            if data is not None:
                data["queries"]["request"][0]["searchTerms"] = data["queries"]["request"][0]["searchTerms"][1:-1]
        except (KeyError, IndexError):
            raise DSInvalidResource("Google Image resource does not specify searchTerms", self)
        return content_type, data

    def next_parameters(self):
        if self.request["quantity"] <= 0:
            return {}
        content_type, data = super(GoogleImage, self).content
        missing_quantity = self.request["quantity"] - 10
        try:
            next_data = data["queries"]["nextPage"][0]
        except KeyError:
            return {}
        return {
            "start": next_data["startIndex"],
            "quantity": missing_quantity
        }

    def _create_request(self, method, *args, **kwargs):
        request = super(GoogleImage, self)._create_request(method, *args, **kwargs)
        request["quantity"] = self.variables(*args)["quantity"]
        return request

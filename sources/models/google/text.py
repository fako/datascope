from core.exceptions import DSInvalidResource
from sources.models.google.query import GoogleQuery


class GoogleText(GoogleQuery):

    URI_TEMPLATE = 'https://www.googleapis.com/customsearch/v1?q={}'
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
            "quantity": args[2] if len(args) > 2 else 0,
        }

    def auth_parameters(self):
        params = super(GoogleText, self).auth_parameters()
        params.update({
            "cx": self.config.cx
        })
        return params

    @property
    def content(self):
        content_type, data = super(GoogleText, self).content
        try:
            if data is not None:
                data["queries"]["request"][0]["searchTerms"] = data["queries"]["request"][0]["searchTerms"][1:-1]
        except (KeyError, IndexError):
            raise DSInvalidResource("Google Image resource does not specify searchTerms", self)
        return content_type, data

    def next_parameters(self):
        if self.request["quantity"] <= 0:
            return {}
        content_type, data = super(GoogleText, self).content
        missing_quantity = self.request["quantity"] - 10
        try:
            nextData = data["queries"]["nextPage"][0]
        except KeyError:
            return {}
        return {
            "start": nextData["startIndex"],
            "quantity": missing_quantity
        }

    def _create_request(self, method, *args, **kwargs):
        request = super(GoogleText, self)._create_request(method, *args, **kwargs)
        request["quantity"] = self.variables(*args)["quantity"]
        return request

from core.exceptions import DSInvalidResource, DSHttpError400NoToken

from sources.models.wikipedia.query import WikipediaAPI


class WikipediaToken(WikipediaAPI):

    URI_TEMPLATE = "https://{}.wikipedia.org/w/api.php"

    DATA = {
        "action": "query",
        "format": "json",
        "utf8": "",
        "meta": "tokens",
        "type": ""  # gets set at runtime
    }

    POST_SCHEMA = {
        "args": {
            "title": "token arguments",
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "[a-z]{2}"
                }
            ],
            "additionalItems": False,
            "minItems": 1
        },
        "kwargs": {
            "title": "token keyword arguments",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["login", "csrf"]

                }
            },
            "required": ["type"]
        }
    }

    def post(self, *args, **kwargs):
        kwargs["type"] = args[0]  # sets token type
        args = (self.config.wiki_country,)
        return super(WikipediaAPI, self).post(*args, **kwargs)

    def get_token(self):
        content_type, data = self.content
        return data["query"]["tokens"].get(self.request["data"]["type"] + "token")

    def _handle_errors(self):
        super(WikipediaAPI, self)._handle_errors()

        # Check general response
        content_type, data = self.content
        if "query" not in data:
            raise DSInvalidResource('Wrongly formatted Wikipedia response, missing "query"', resource=self)
        response = data['query']["tokens"]  # Wiki has response hidden under single keyed dicts :(
        if not response:
            raise DSInvalidResource('Wikipedia response is empty', resource=self)

    def get(self, *args, **kwargs):
        raise NotImplementedError("GET is not implemented for this resource")


class WikipediaLogin(WikipediaAPI):

    URI_TEMPLATE = "https://{}.wikipedia.org/w/api.php"

    DATA = {
        "action": "login",
        "format": "json",
        "utf8": "",
        "lgtoken": "",
        "lgname": "",
        "lgpassword": ""
    }

    POST_SCHEMA = {
        "args": {
            "title": "login arguments",
            "type": "array",
            "items": [
                {
                    "type": "string",
                    "pattern": "[a-z]{2}"
                }
            ],
            "additionalItems": False,
            "minItems": 1
        },
        "kwargs": {
            "title": "token keyword arguments",
            "type": "object",
            "properties": {
                "lgname": {
                    "type": "string",
                },
                "lgpassword": {
                    "type": "string",
                }
            },
            "required": ["lgname", "lgpassword"]
        }
    }

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        super(WikipediaLogin, self).__init__(*args, **kwargs)

    def data(self, **kwargs):
        data = super(WikipediaLogin, self).data(**kwargs)
        if not self.token:
            raise DSHttpError400NoToken(
                "No login token specified for WikipediaLogin. Use WikipediaToken to fetch one",
                resource=self
            )
        data["lgtoken"] = self.token
        return data

    def parameters(self, **kwargs):
        parameters = dict(self.PARAMETERS)
        parameters.pop("continue", None)
        return parameters

    def post(self, *args, **kwargs):
        args = (self.config.wiki_country,)
        kwargs["lgname"] = kwargs.pop("username", kwargs.get("lgname"))
        kwargs["lgpassword"] = kwargs.pop("password", kwargs.get("lgpassword"))
        return super(WikipediaLogin, self).post(*args, **kwargs)

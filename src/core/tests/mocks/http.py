from unittest.mock import Mock

from django.db.models import QuerySet

from datagrowth.resources import HttpResource
from core.tests.mocks.requests import MockRequests


MockErrorQuerySet = Mock(QuerySet)
MockErrorQuerySet.count = Mock(return_value=0)


class HttpResourceMock(HttpResource):

    URI_TEMPLATE = "http://localhost:8000/{}/?q={}"
    PARAMETERS = {
        "param": 1
    }
    HEADERS = {
        "Accept": "application/json"
    }
    GET_SCHEMA = {
        "args": {
            "title": "resource mock arguments",
            "type": "array",  # a single alphanumeric element
            "items": [
                {
                    "type": "string",
                    "enum": ["en", "nl"]
                },
                {
                    "type": "string",
                    "pattern": "[A-Za-z0-9]+"
                }
            ],
            "additionalItems": False,
            "minItems": 2
        },
        "kwargs": None  # not allowed
    }
    POST_SCHEMA = {
        "args": {
            "title": "resource mock arguments",
            "type": "array",  # a single alphanumeric element
            "items": [
                {
                    "type": "string",
                    "enum": ["en", "nl"]
                },
                {
                    "type": "string",
                    "pattern": "[A-Za-z0-9]+"
                }
            ],
            "additionalItems": False,
            "minItems": 2
        },
        "kwargs": {
            "title": "resource mock keyword arguments",
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }

    CONFIG_NAMESPACE = "mock"

    def __init__(self, *args, **kwargs):
        super(HttpResourceMock, self).__init__(*args, **kwargs)
        self.session = MockRequests
        self.session.send.reset_mock()

    def send(self, method, *args, **kwargs):
        if method == "post":
            query = kwargs.get("query")
            if query:
                args += (query,)
            args = (self.config.source_language,) + args
        elif method == "get":
            args = (self.config.source_language,) + args
        return super(HttpResourceMock, self).send(method, *args, **kwargs)

    def auth_parameters(self):
        return {
            "auth": 1,
            "key": self.config.secret
        }

    def next_parameters(self):
        content_type, data = self.content
        try:
            nxt = data["next"]
        except (KeyError, TypeError):
            return {}
        return {"next": nxt}

    @property
    def meta(self):
        return self.variables()["meta"]

    def data(self, **kwargs):
        return {
            "test": kwargs.get("query")
        }

    def variables(self, *args):
        args = args or (self.request["args"] if self.request else tuple())
        return {
            "url": args,
            "meta": args[1] if len(args) > 1 else None
        }

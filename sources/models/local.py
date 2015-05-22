from datascope.configuration import MOCK_CONFIGURATION

from core.models.resources.http import HttpResource
from core.utils import configuration
from core.tests.mocks import MockRequests


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
        "args": {},
        "kwargs": {}
    }

    config = configuration.ConfigurationField(
        config_defaults=MOCK_CONFIGURATION,
        namespace="mock"
    )

    def __init__(self, *args, **kwargs):
        super(HttpResourceMock, self).__init__(*args, **kwargs)
        self.session = MockRequests
        self.session.send.reset_mock()

    def send(self, method, *args, **kwargs):
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
    def query(self):
        try:
            return self.request["args"][1]
        except (KeyError, IndexError, TypeError):
            return None

    @property
    def input_for_organism(self):
        content_type, data = self.content
        return self.query, content_type, data

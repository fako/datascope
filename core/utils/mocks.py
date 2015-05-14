import json

import requests
from requests.models import Response
from mock import Mock, NonCallableMock


class MockDefaults(object):  # TODO: make it a dict

    # testing basic functionality
    name_namespace_configuration = "namespace configuration"
    global_global_configuration = "global configuration"

    # mock configuration for testing HttpResourceMock
    global_source_language = "en"
    mock_secret = "oehhh"


MOCK_DATA = {
    "dict": {
        "test": "nested value",
        "list": ["nested value 0", "nested value 1", "nested value 2"],
        "dict": {"test": "test"}
    },
    "list": ["value 0", "value 1", "value 2"],
    "dotted.key": "another value",
    "next": 1
}


MockRequests = NonCallableMock(spec=requests)
response = NonCallableMock(spec=Response)
response.headers = {"Content-Type": "application/json"}
response.content = json.dumps(MOCK_DATA)
response.status_code = 200
MockRequestsGet = Mock(return_value=response)
MockRequests.get = MockRequestsGet

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


MockRequests = NonCallableMock(spec=requests)
response = NonCallableMock(spec=Response)
response.headers = {"ContentType": "application/json"}
response.content = '{"data": 1}'
response.status_code = 200
MockRequestsGet = Mock(return_value=response)
MockRequests.get = MockRequestsGet

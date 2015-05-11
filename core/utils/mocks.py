from mocks import Mock
from requests.models import Response


class MockDefaults(object):  # TODO: make it a dict

    # testing basic functionality
    name_namespace_configuration = "namespace configuration"
    global_global_configuration = "global configuration"

    # mock configuration for testing HttpResourceMock
    global_source_language = "en"
    mock_secret = "oehhh"


class MockResponse(object)
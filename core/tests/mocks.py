import json
from copy import deepcopy

import requests
from requests.models import Response
from mock import Mock, NonCallableMock


MOCK_DATA = {
    "dict": {
        "test": "nested value",
        "list": ["nested value 0", "nested value 1", "nested value 2"],
        "dict": {"test": "test"}
    },
    "list": ["value 0", "value 1", "value 2"],
    "dotted.key": "another value",
}


MOCK_DATA_WITH_NEXT = deepcopy(MOCK_DATA)
MOCK_DATA_WITH_NEXT["next"] = 1


standard_response = NonCallableMock(spec=Response)
standard_response.headers = {"Content-Type": "application/json"}
standard_response.content = json.dumps(MOCK_DATA)
standard_response.status_code = 200


MockRequests = NonCallableMock(spec=requests)
MockRequestsGet = Mock(return_value=standard_response)
MockRequests.get = MockRequestsGet
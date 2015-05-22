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


ok_response = NonCallableMock(spec=Response)
ok_response.headers = {"Content-Type": "application/json"}
ok_response.content = json.dumps(MOCK_DATA)
ok_response.status_code = 200


agent_response = NonCallableMock(spec=Response)
agent_response.headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla /5.0 (Compatible MSIE 9.0;Windows NT 6.1;WOW64; Trident/5.0)"
}
agent_response.content = json.dumps(MOCK_DATA)
agent_response.status_code = 200


not_found_response = NonCallableMock(spec=Response)
not_found_response.headers = {"Content-Type": "application/json"}
not_found_response.content = json.dumps({"error": "not found"})
not_found_response.status_code = 404


error_response = NonCallableMock(spec=Response)
error_response.headers = {"Content-Type": "application/json"}
error_response.content = json.dumps({"error": "internal error"})
error_response.status_code = 500


def return_get_response(url, headers, proxies):
    if "404" in url:
        return not_found_response
    elif "500" in url:
        return error_response
    else:
        return ok_response


MockRequests = NonCallableMock(spec=requests)
MockRequestsGet = Mock(side_effect=return_get_response)
MockRequests.get = MockRequestsGet


MockRequestsWithAgent = NonCallableMock(spec=requests)
MockRequestsGetWithAgent = Mock(return_value=agent_response)
MockRequestsWithAgent.get = MockRequestsGetWithAgent

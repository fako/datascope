from __future__ import unicode_literals, absolute_import, print_function, division

import json

import requests
from requests.models import Response

from mock import Mock, NonCallableMock

from core.tests.mocks.data import MOCK_DATA


ok_response = NonCallableMock(spec=Response)
ok_response.headers = {"content-type": "application/json"}
ok_response.content = json.dumps(MOCK_DATA)
ok_response.status_code = 200

agent_response = NonCallableMock(spec=Response)
agent_response.headers = {
    "content-type": "application/json",
    "User-Agent": "Mozilla /5.0 (Compatible MSIE 9.0;Windows NT 6.1;WOW64; Trident/5.0)"
}
agent_response.content = json.dumps(MOCK_DATA)
agent_response.status_code = 200

not_found_response = NonCallableMock(spec=Response)
not_found_response.headers = {"content-type": "application/json"}
not_found_response.content = json.dumps({"error": "not found"})
not_found_response.status_code = 404

error_response = NonCallableMock(spec=Response)
error_response.headers = {"content-type": "application/json"}
error_response.content = json.dumps({"error": "internal error"})
error_response.status_code = 500


def prepare_request(request):
    return requests.Session().prepare_request(request)


def return_response(prepared_request, proxies, verify, timeout):
    if "404" in prepared_request.url:
        return not_found_response
    elif "500" in prepared_request.url:
        return error_response
    else:
        return ok_response


MockRequests = NonCallableMock(spec=requests)
MockRequestsSend = Mock(side_effect=return_response)
MockRequests.send = MockRequestsSend
MockRequests.prepare_request = Mock(side_effect=prepare_request)

MockRequestsWithAgent = NonCallableMock(spec=requests)
MockRequestsSendWithAgent = Mock(return_value=agent_response)
MockRequestsWithAgent.send = MockRequestsSendWithAgent
MockRequestsWithAgent.prepare_request = Mock(side_effect=prepare_request)

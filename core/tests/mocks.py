# coding=utf-8
from __future__ import unicode_literals, absolute_import, print_function, division

import json
from copy import deepcopy

import requests
from requests.models import Response
from mock import Mock, NonCallableMock
from celery import Task


MOCK_DATA = {
    "dict": {
        "test": "nested value",
        "list": ["nested value 0", "nested value 1", "nested value 2"],
        "dict": {"test": "test"}
    },
    "list": ["value 0", "value 1", "value 2"],
    "dotted.key": "another value",
    "unicode": ["überhaupt"]
}
MOCK_DATA_WITH_NEXT = deepcopy(MOCK_DATA)
MOCK_DATA_WITH_NEXT["next"] = 1


MOCK_HTML = """
<!doctype html>
<html>

<head>
    <title>Test</title>
</head>

<body>

</body>

<div id="content">
    <p>
        A list with links:
        <ul>
            <li><a href="/test">test</a></li>
            <li><a href="/test2">test 2</a></li>
            <li><a href="/test3">test 3</a></li>
            <li>That's it!</li>
        </ul>
    </p>
</div>

</html>
"""
MOCK_SCRAPE_DATA = [
    {'text': 'test', 'link': '/test', 'page': 'Test'},
    {'text': u'test 2', 'link': '/test2', 'page': 'Test'},
    {'text': u'test 3', 'link': '/test3', 'page': 'Test'}
]


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


def return_response(prepared_request, proxies, verify):
    if "404" in prepared_request.url:
        return not_found_response
    elif "500" in prepared_request.url:
        return error_response
    else:
        return ok_response


MockRequests = NonCallableMock(spec=requests)
MockRequestsSend = Mock(side_effect=return_response)
MockRequests.send = MockRequestsSend


MockRequestsWithAgent = NonCallableMock(spec=requests)
MockRequestsSendWithAgent = Mock(return_value=agent_response)
MockRequestsWithAgent.send = MockRequestsSendWithAgent

MockTask = Mock(spec=Task)
MockTask.s = Mock(return_value=Task())
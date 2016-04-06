import json
from pprint import pformat

from django.shortcuts import HttpResponse
from django.views.decorators import csrf, http
from django.core.mail import mail_managers


def index(request):
    return HttpResponse("Datascope version 0.3 (Python 3)")


@http.require_http_methods(["OPTIONS", "POST"])
@csrf.csrf_exempt
def question(request):
    if request.method == "OPTIONS":
        return HttpResponse('options')
    data = json.loads(request.body.decode('utf-8'))
    text = pformat(data, indent=4)
    mail_managers(data['question'], text)
    return HttpResponse('send')

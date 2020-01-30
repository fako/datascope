import json
from pprint import pformat

from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators import csrf, http
from django.core.mail import mail_managers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, schema, permission_classes
from rest_framework.permissions import AllowAny


def index(request):
    return HttpResponse("Datascope version {} (Python 3)".format(settings.DATASCOPE_VERSION))


@http.require_http_methods(["OPTIONS", "POST"])
@csrf.csrf_exempt
def question(request):
    if request.method == "OPTIONS":
        return HttpResponse('options')
    data = json.loads(request.body.decode('utf-8'))
    text = pformat(data, indent=4)
    mail_managers(data['question'], text)
    return HttpResponse('send')


@api_view()
@permission_classes([AllowAny])
@schema(None)
def health_check(request):
    return Response({"healthy" : True}, status.HTTP_200_OK)

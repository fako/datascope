# Create your views here.
import json
from pprint import pformat

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import mail_managers


@csrf_exempt  # TODO: patch this leak
def question(request):
    if request.method == 'POST':  # TODO: wtf, ugly as hell
        data = json.loads(request.body)
        text = pformat(data, indent=4)
        mail_managers(data['question'], text)
        return HttpResponse('send')
    return HttpResponse('options')
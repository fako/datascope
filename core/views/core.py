from django.shortcuts import HttpResponse, render_to_response


def index(request):
    return HttpResponse("Datascope version 0.3 (Python 3)")
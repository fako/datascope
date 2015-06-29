from __future__ import unicode_literals, absolute_import, print_function, division

from copy import copy

from django.core.exceptions import ValidationError
from django.shortcuts import render_to_response, RequestContext
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

from core.models.organisms.community import CommunityState
from core.exceptions import DSProcessUnfinished, DSProcessError


class CommunityView(APIView):
    """

    """

    RESPONSE_DATA = {
        "actions": [],  # FEATURE: get all available actions
        "status": {},  # FEATURE: get the status of growth
        "result": {},
        "results": [],
        "error": None
    }

    def get(self, request, community_class, path="", *args, **kwargs):
        response_data = copy(self.RESPONSE_DATA)
        community, created = community_class.get_or_create_by_input(*path.split('/'), **request.GET.dict())

        if community.state == CommunityState.SYNC:
            # FEATURE: set status
            return Response(response_data, HTTP_202_ACCEPTED)
        try:
            community.grow()
        except ValidationError as exc:
            response_data["error"] = exc
            return Response(response_data, HTTP_400_BAD_REQUEST)
        except DSProcessUnfinished:
            # FEATURE: set status
            return Response(response_data, HTTP_202_ACCEPTED)
        except DSProcessError:
            # FEATURE: set errors
            return Response(response_data, HTTP_500_INTERNAL_SERVER_ERROR)

        manifestation = community.manifestation
        if not manifestation:
            return Response(None, HTTP_204_NO_CONTENT)
        results_key = "results" if isinstance(manifestation, list) else "result"
        response_data[results_key] = manifestation
        return Response(response_data, HTTP_200_OK)

    # FEATURE: allow actions who's function lives on a Community through POST
    # def post(self, request, action, community_class, *args, **kwargs):
    #     pass


class HtmlCommunityView(View):

    INDEX = "index.html"
    ACCEPTED = "accepted.html"
    OK = "ok.html"
    NO_CONTENT = "no-content.html"
    BAD_REQUEST = "bad-request.html"
    MULTIPLE_CHOICES = "multiple-choices.html"

    @staticmethod
    def html_template_for(community_class, response):
        if response.status_code == 200:
            template = HtmlCommunityView.OK
        elif response.status_code == 202:
            template = HtmlCommunityView.ACCEPTED
        elif response.status_code in [204, 404]:
            template = HtmlCommunityView.NO_CONTENT
        elif response.status_code == 300:
            template = HtmlCommunityView.MULTIPLE_CHOICES
        elif response.status_code == 400:
            template = HtmlCommunityView.BAD_REQUEST
        else:
            template = HtmlCommunityView.INDEX
        return '{}/{}'.format(community_class.get_name(), template)

    @staticmethod
    def data_for(community_class, response):
        if response.status_code == 200:
            return response.data
        elif response.status_code == 300:
            return response.data
        return None

    def get(self, request, community_class, path="", *args, **kwargs):
        api_response = CommunityView().get(request, community_class, path, *args, **kwargs)
        template_context = {
            'self_reverse': community_class.get_name() + '-plain',
            'response': self.data_for(community_class, api_response)
        }
        return render_to_response(
            self.html_template_for(community_class, api_response),
            template_context,
            RequestContext(request)
        )

from __future__ import unicode_literals, absolute_import, print_function, division
import six
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlencode

from copy import copy

from django.core.exceptions import ValidationError
from django.shortcuts import render_to_response, RequestContext, Http404
from django.views.generic import View
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

from core.models.organisms.community import CommunityState, Manifestation
from core.exceptions import DSProcessUnfinished, DSProcessError
from core.utils.helpers import parse_datetime_string


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

    def _get_response_from_manifestation(self, manifestation, response_data):
        manifestation_data = manifestation.get_data()
        if not manifestation_data:
            return Response(None, HTTP_204_NO_CONTENT)
        results_key = "results" if isinstance(manifestation_data, list) else "result"
        response_data[results_key] = manifestation_data
        return Response(response_data, HTTP_200_OK)

    def _get_data_response(self, community_class, query_path, query_parameters, full_path):
        response_data = copy(self.RESPONSE_DATA)

        try:
            manifestation = Manifestation.objects.get(uri=full_path)
            community = manifestation.community
        except Manifestation.DoesNotExist:
            manifestation = None
            signature = community_class.get_signature_from_input(
                *query_path.split('/'),
                **query_parameters
            )
            created_at = parse_datetime_string(query_parameters.get("t", None))
            if "t" not in query_parameters:
                community, created = community_class.objects.get_or_create_by_signature(
                    signature,
                    **query_parameters
                )
            elif created_at is not None:
                community = community_class.objects.get(
                    signature=signature,
                    created_at=created_at
                )
                community.config = community_class.get_configuration_from_input(**query_parameters)
            else:
                raise Http404("Can not find community with t={}".format(query_parameters.get("t")))

        try:

            if manifestation is not None:
                return self._get_response_from_manifestation(manifestation, response_data)
            if community.state == CommunityState.SYNC:
                raise DSProcessUnfinished()

            community.grow(*query_path.split('/'))
            config = Manifestation.generate_config(community.PUBLIC_CONFIG, **query_parameters)
            manifestation = Manifestation.objects.create(uri=full_path, community=community, config=config)
            return self._get_response_from_manifestation(manifestation, response_data)

        except ValidationError as exc:
            response_data["error"] = exc
            return Response(response_data, HTTP_400_BAD_REQUEST)

        except DSProcessUnfinished:
            # FEATURE: set status
            return Response(response_data, HTTP_202_ACCEPTED)

        except DSProcessError:
            # FEATURE: set errors
            return Response(response_data, HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, community_class, path="", *args, **kwargs):
        return self._get_data_response(
            community_class,
            query_path=path,
            query_parameters=request.GET.dict(),
            full_path=request.get_full_path()
        )

    def get_service_data_response(self, community_class, query_path, query_parameters):
        assert isinstance(query_parameters, dict), \
            "query_parameters for get_service_data_response should be a dictionary without urlencoded values"
        service_view = "v1:{}_service".format(community_class.get_name())
        # Order of the given parameters matters
        # for database lookups of previously calculated results for these parameters
        parameters_sorted_by_keys = sorted(six.iteritems(query_parameters), key=lambda item: item[0])
        full_path = "{}?{}".format(
            reverse(service_view, kwargs={"path": query_path}),
            "&".join("{}={}".format(key, value) for key, value in parameters_sorted_by_keys)
        )
        return self._get_data_response(
            community_class,
            query_path=query_path,
            query_parameters=query_parameters,
            full_path=full_path
        )

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

    def get(self, request, community_class, path=None, *args, **kwargs):
        # Index request
        if path is None and community_class.INPUT_THROUGH_PATH:
            return render_to_response(
                "{}/{}".format(community_class.get_name(), HtmlCommunityView.INDEX),
                {},
                RequestContext(request)
            )
        # Search request
        api_response = CommunityView().get_service_data_response(community_class, path, request.GET.dict())
        template_context = {
            'self_reverse': community_class.get_name() + '_html',
            'response': self.data_for(community_class, api_response)
        }
        return render_to_response(
            self.html_template_for(community_class, api_response),
            template_context,
            RequestContext(request)
        )

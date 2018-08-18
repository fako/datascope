import warnings
from copy import copy

from django.core.exceptions import ValidationError
from django.shortcuts import Http404
from django.template.response import TemplateResponse
from django.views.generic import View
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

from core.models.organisms.states import CommunityState
from core.models.resources.manifestation import Manifestation
from core.exceptions import DSProcessUnfinished, DSProcessError
from core.utils.helpers import parse_datetime_string, format_datetime
from core.utils.configuration import get_standardized_configuration


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

    @classmethod
    def _get_response_from_manifestation(cls, manifestation):
        response_data = copy(cls.RESPONSE_DATA)
        manifestation_data = manifestation.get_data(async=manifestation.community.ASYNC_MANIFEST)
        if not manifestation_data:
            return Response(None, HTTP_204_NO_CONTENT)
        results_key = "results" if isinstance(manifestation_data, list) else "result"
        response_data[results_key] = manifestation_data
        return Response(response_data, HTTP_200_OK)

    @classmethod
    def _get_response_from_error(cls, error_message, status_code):
        response_data = copy(cls.RESPONSE_DATA)
        response_data["error"] = error_message
        return Response(response_data, status_code)

    @classmethod
    def get_configuration_from_request(cls, request):
        get_configuration = request.GET.dict()
        post_configuration = request.data.get("config", {}) if hasattr(request, 'data') else {}
        for get_parameter in get_configuration:
            if get_parameter in post_configuration:
                raise ValidationError( "{} should be specified in either GET and POST not both".format(get_parameter))
        configuration = dict(**get_configuration, **post_configuration)
        for key, value in configuration.items():
            if isinstance(value, str) and value.isnumeric() and not key == "t":
                configuration[key] = float(value) if "." in key else int(value)
        try:
            created_at_parameter = configuration.pop("t")
            warnings.warn("The t parameter to retrieve older communities is deprecated. Use the versions view instead.",
                          DeprecationWarning)
        except KeyError:
            return configuration, (None, None,)
        return configuration, (created_at_parameter, parse_datetime_string(created_at_parameter),)

    @classmethod
    def get_full_path(cls, community_class, query_path, configuration=None, created_at=None):
        warnings.warn("CommunityView.get_full_path is deprecated in favor of get_uri", DeprecationWarning)
        configuration = configuration or {}
        service_view_name = "v1:{}_service".format(community_class.get_name())
        service_view_url = reverse(service_view_name, kwargs={"path": query_path})
        if created_at:
            configuration["t"] = format_datetime(created_at)
        config_query = "?" + get_standardized_configuration(configuration, as_hash=False) if configuration else ""
        return service_view_url + config_query

    @classmethod
    def get_uri(cls, community_class, query_path, configuration=None, created_at=None):
        simple_configuration = {
            key: value for key, value in configuration.items() if isinstance(value, (int, float, str, bool))
        }
        service_view_name = "v1:{}_service".format(community_class.get_name())
        service_view_url = reverse(service_view_name, kwargs={"path": query_path})
        if created_at:
            configuration["t"] = format_datetime(created_at)
        query = "?" + get_standardized_configuration(simple_configuration, as_hash=False) if configuration else ""
        anchor = "#" + get_standardized_configuration(configuration) if configuration else ""
        return service_view_url + query + anchor

    def get_response(self, community_class, query_path, configuration, created_at_info=(None, None)):
        assert isinstance(configuration, dict), \
            "configuration for get_response should be a dictionary without urlencoded values"

        created_at_parameter, created_at = created_at_info
        uri = CommunityView.get_uri(community_class, query_path, configuration, created_at)

        try:
            manifestation = Manifestation.objects.get(uri=uri)
            community = manifestation.community
        except Manifestation.DoesNotExist:
            manifestation = None
            signature = community_class.get_signature_from_input(
                *query_path.split('/'),
                **configuration
            )
            if created_at is None:
                community, created = community_class.objects.get_latest_or_create_by_signature(
                    signature,
                    **configuration
                )
            else:
                try:
                    community = community_class.objects.get(signature=signature, created_at=created_at)
                    community.config = community_class.filter_growth_configuration(**configuration)
                except community_class.DoesNotExist:
                    raise Http404("Can not find community with t={}".format(created_at_parameter))

        try:

            if manifestation is not None:
                return self._get_response_from_manifestation(manifestation)
            if community.state == CommunityState.SYNC:
                raise DSProcessUnfinished()

            community.grow(*query_path.split('/'))
            config = community.filter_scope_configuration(**configuration)
            manifestation = Manifestation.objects.create(uri=uri, community=community, config=config)
            return self._get_response_from_manifestation(manifestation)

        except ValidationError as exc:
            return self._get_response_from_error(exc.message, HTTP_400_BAD_REQUEST)

        except DSProcessUnfinished:
            # FEATURE: set status
            response_data = copy(self.RESPONSE_DATA)
            return Response(response_data, HTTP_202_ACCEPTED)

        except DSProcessError as exc:
            # TODO: log exception
            return self._get_response_from_error(str(exc), HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, community_class, path="", *args, **kwargs):
        configuration, created_at_info = self.get_configuration_from_request(request)
        return self.get_response(
            community_class,
            query_path=path,
            configuration=configuration,
            created_at_info=created_at_info
        )

    def post(self, request, community_class, path="", *args, **kwargs):
        action = request.data.get("action")
        if action != "manifest" and action != "scope":
            # FEATURE: allow actions who's function lives on a Community through POST
            error = "{} is an unknown action".format(action)
            return self._get_response_from_error(error, HTTP_400_BAD_REQUEST)

        configuration, created_at_info = self.get_configuration_from_request(request)

        return self.get_response(
            community_class,
            query_path=path,
            configuration=configuration,
            created_at_info=created_at_info
        )


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
    def data_for(community_class, response=None):
        if response is None:
            return None
        if response.status_code == 200:
            return response.data
        elif response.status_code == 300:
            return response.data
        elif response.status_code == 400:
            return response.data
        return None

    def get(self, request, community_class, path=None, *args, **kwargs):
        # Index request
        if path is None and community_class.INPUT_THROUGH_PATH:
            return TemplateResponse(
                request,
                "{}/{}".format(community_class.get_name(), HtmlCommunityView.INDEX),
                context={
                    'self_reverse': community_class.get_name() + '_html',
                    'response': self.data_for(community_class)
                }
            )
        elif path is None:
            path = ""
        # Search request

        api_view = CommunityView()
        configuration, created_at_info = api_view.get_configuration_from_request(request)
        api_response = api_view.get_response(
            community_class,
            path,
            configuration,
            created_at_info
        )
        template_context = {
            'self_reverse': community_class.get_name() + '_html',
            'response': self.data_for(community_class, api_response)
        }
        return TemplateResponse(
            request,
            self.html_template_for(community_class, api_response),
            context=template_context,
        )

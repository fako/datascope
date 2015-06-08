from copy import copy

from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

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

    def get(self, request, path, community_class, *args, **kwargs):
        response_data = copy(self.RESPONSE_DATA)
        community, created = community_class.get_or_create_by_input(*path.split('/'), **request.GET.dict())
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

        manifestation = community.manifestation()
        if not manifestation:
            return Response(None, HTTP_204_NO_CONTENT)
        results_key = "results" if isinstance(manifestation, list) else "result"
        response_data[results_key] = manifestation
        return Response(response_data, HTTP_200_OK)

    # FEATURE: allow actions who's function lives on a Community through POST
    # def post(self, request, action, community_class, *args, **kwargs):
    #     pass


class PlainCommunityView(CommunityView):
    pass
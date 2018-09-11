import re

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.views import CommunityView

from future_fashion.models import InventoryCommunity


hex_color_pattern = re.compile("^[A-F0-9]{6}$")


@api_view(["POST", "OPTIONS"])
def swipe_interface_view(request):

    def format_data(entry):
        return {
            "id": entry["id"],
            "url": entry["path"].replace("future_fashion/data", "")
        }

    api_view = CommunityView()
    configuration, created_at_info = api_view.get_configuration_from_request(request)

    # Checking validity of request
    for parameter in ["$top", "$bottom", "$accessories"]:
        # Check required configuration
        if parameter not in configuration:
            return Response(
                {"error": "The {} query parameter is required".format(parameter)}, status.HTTP_400_BAD_REQUEST
            )
        # Checking parameters and converting if necessary
        parameter_value = configuration[parameter]
        if parameter_value.startswith("#"):
            parameter_value = parameter_value[1:]
        if not hex_color_pattern.match(parameter_value):
            return Response(
                {"error": "The {} query parameter should be a hex color".format(parameter)}, status.HTTP_400_BAD_REQUEST
            )
        # Converting hex colors to rgb
        configuration[parameter] = ",".join(
            str(int(parameter_value[i:i+2], 16))
            for i in (0, 2, 4)
        )

    # We're dealing with a valid request. Get the data.
    api_response = api_view.get_response(
        InventoryCommunity,
        "pilot",
        configuration,
        created_at_info
    )
    if not api_response.status_code == status.HTTP_200_OK:
        return api_response
    data = iter(api_response.data["results"])

    # Now check exactly what data was asked for
    _id = request.data.get("id", None)
    like = request.data.get("like", None)
    score = request.data.get("score", None)

    if _id and like is not None and score is not None:
        if not isinstance(_id, int) and not _id.isnumeric() or not isinstance(like, int) and not like.isnumeric() or \
                not isinstance(score, float) and not score.isnumeric():
            return Response(
                {"error": "The id, like and score parameters should be numbers"}, status.HTTP_400_BAD_REQUEST
            )

        while next(data)["id"] != int(_id):
            pass

    # Return the data unless it is exhausted
    try:
        return Response(format_data(next(data)), status.HTTP_200_OK)
    except StopIteration:
        return Response({}, status.HTTP_204_NO_CONTENT)

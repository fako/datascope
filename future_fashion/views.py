import re

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.views import CommunityView

from future_fashion.models import ClothingInventoryCommunity


hex_color_pattern = re.compile("^[A-Fa-z0-9]{6}$")


@api_view(["POST", "OPTIONS"])
def swipe_interface_view(request):

    def format_data(entry):
        return {
            "id": entry["id"],
            "url": request.build_absolute_uri(entry["path"].replace("future_fashion/data", "")),
            "type": entry["type"]
        }

    # Standard request validation
    _id = request.data.get("id", None)
    like = request.data.get("like", None)
    score = request.data.get("score", None)
    type = request.GET.get("type", None)
    if not type:
        return Response(
            {"error": "Type is a required parameter"}, status.HTTP_400_BAD_REQUEST
        )
    if _id and like is not None and score is not None:
        # A post with set _id should have valid like and score as well
        if not isinstance(_id, int) and not _id.isnumeric() or not isinstance(like, int) and not like.isnumeric() or \
                not isinstance(score, float) and not score.isnumeric():
            return Response(
                {"error": "The id, like and score parameters should be numbers"}, status.HTTP_400_BAD_REQUEST
            )

    # API request validation
    api_view = CommunityView()
    configuration, created_at_info = api_view.get_configuration_from_request(request)
    configuration.update({
        "brighten": 50,
        "remove_background": 1
    })
    for parameter in ["$top", "$bottom"]:
        # Check required configuration
        if parameter not in configuration:
            return Response(
                {"error": "The {} query parameter is required".format(parameter)}, status.HTTP_400_BAD_REQUEST
            )
        # Checking parameters and converting if necessary
        parameter_value = str(configuration[parameter])
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
        ClothingInventoryCommunity,
        "pilot",
        configuration,
        created_at_info
    )
    if not api_response.status_code == status.HTTP_200_OK:
        return api_response
    data = [entry for entry in api_response.data["results"] if entry["type"] == type]
    if not _id:
        return Response(format_data(data[0]), status.HTTP_200_OK)

    # Figure out next object to return
    # Should act like a carousel
    # Initial position comes from _id
    ixs = [entry["id"] for entry in data]
    ix = ixs.index(_id)
    if like:
        ix += 1
    else:
        ix -= 1
    if ix < 0:
        ix = len(ixs) - 1
    else:
        ix %= len(ixs)

    return Response(format_data(data[ix]), status.HTTP_200_OK)

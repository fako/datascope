import os
import json

from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST", "OPTIONS"])
def swipe_interface_view(request):

    def format_data(entry):
        return {
            "id": entry["id"],
            "url": entry["path"].replace("system/files/", "")
        }

    with open(os.path.join(settings.PATH_TO_PROJECT, "future_fashion", "results", "little-french-dress.json")) as file:
        data = iter(json.load(file))

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

    try:
        return Response(format_data(next(data)), status.HTTP_200_OK)
    except StopIteration:
        return Response({}, status.HTTP_204_NO_CONTENT)

import os
import json

from django.template.response import TemplateResponse
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.views.community import HtmlCommunityView


class FutureFashionHtmlView(HtmlCommunityView):

    def get(self, request, community_class, path=None, *args, **kwargs):
        if not "$reference" in request.GET:
            community = community_class.objects.last()
            results = []
            for ind in community.kernel.individual_set.all()[:10]:
                ind.properties["id"] = ind.id
                results.append(ind.properties)
            return TemplateResponse(
                request,
                "{}/{}".format(community_class.get_name(), HtmlCommunityView.OK),
                {
                    'response': {
                        'results': results
                    }
                }
            )
        return super(FutureFashionHtmlView, self).get(request, community_class, path=path, *args, **kwargs)


@api_view(["GET", "POST"])
def swipe_interface_view(request):

    def format_data(entry):
        return {
            "id": entry["id"],
            "url": request.build_absolute_uri(entry["path"].replace("system/files", ""))
        }

    with open(os.path.join(settings.PATH_TO_PROJECT, "future_fashion", "results", "little-french-dress.json")) as file:
        data = iter(json.load(file))

    if request.method == "POST":

        _id = request.GET.get("id", None)
        like = request.GET.get("like", None)
        score = request.GET.get("score", None)
        if not _id or not like or not score or _id == "null" or like == "null" or score == "null":
            return Response(
                {"error": "The id, like and score parameters should be set when using POST"},
                status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(_id, int) and not _id.isnumeric() or not isinstance(like, int) and not like.isnumeric() or \
                not isinstance(score, int) and not score.isnumeric():
            return Response(
                {"error": "The id, like and score parameters should be numbers"}, status.HTTP_400_BAD_REQUEST
            )

        while next(data)["id"] != int(_id):
            pass

    try:
        return Response(format_data(next(data)), status.HTTP_200_OK)
    except StopIteration:
        return Response({}, status.HTTP_204_NO_CONTENT)

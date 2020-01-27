from rest_framework import viewsets
from rest_framework.response import Response

from core.models.organisms.community import CommunityState
from online_discourse.models import DiscourseSearchCommunity


class DiscourseViewSet(viewsets.ViewSet):

    @staticmethod
    def _community_as_dict(community):
        name, configuration = community.get_configuration_module()
        configuration = configuration._asdict() if configuration else {}
        configuration["id"] = community.id
        configuration["name"] = name
        return name, configuration

    def list(self, request):
        english = []
        dutch = []
        for community in DiscourseSearchCommunity.objects.filter(state=CommunityState.READY):
            name, configuration = self._community_as_dict(community)
            language = configuration.get("language", None)
            if language == "en":
                english.append(configuration)
            elif language == "nl":
                dutch.append(configuration)
            elif language is None:
                continue
            else:
                raise AssertionError("Unknown language for {}".format(community.signature))
        return Response({
            "en": english,
            "nl": dutch
        })

    def retrieve(self, request, pk=None):
        community = DiscourseSearchCommunity.objects.get(id=pk)
        name, configuration = self._community_as_dict(community)
        configuration.update(community.aggregates)
        return Response(configuration)

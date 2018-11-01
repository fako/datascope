from urlobject import URLObject

from django.core.mail import mail_managers
from rest_framework import generics, throttling, viewsets
from rest_framework.response import Response

from core.models.organisms.community import CommunityState
from core.utils.data import TextFeaturesFrame
from online_discourse.models import DiscourseSearchCommunity
from online_discourse.models.orders import DiscourseOrderSerializer


class AnonDiscourseOrderThrottle(throttling.AnonRateThrottle):
    rate = "24/day"


class CreateDiscourseOrder(generics.CreateAPIView):
    serializer_class = DiscourseOrderSerializer
    throttle_classes = [AnonDiscourseOrderThrottle]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        mail_managers("discourse order!", "Please check the admin for order details")
        return response


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
        # Set most_important_words
        text_frame = TextFeaturesFrame(
            get_identifier=lambda ind: ind["url"],
            get_text=lambda ind: " ".join([paragraph for paragraph in ind["paragraph_groups"][0]]),
            file_path=community.get_feature_frame_file("text_frame", file_ext=".npz")
        )
        tfidf_sum = text_frame.data.sum(axis=0)
        indices = tfidf_sum.A1.argsort()
        feature_names = text_frame.vectorizer.get_feature_names()
        most_important_words = [feature_names[ix] for ix in indices[-20:]]
        most_important_words.reverse()
        configuration["most_important_words"] = most_important_words
        # Retrieve sets
        authors = set()
        sources = set()
        for individual in community.kernel.content:
            author = individual.get("author", None)
            if author and author.strip():
                authors.add(author)
            url = individual.get("url")
            if url:
                source = URLObject(url).hostname
                if source.startswith('www.'):
                    source = source.replace('www.', '', 1)
                sources.add(source)
        configuration["authors"] = sorted(authors)
        configuration["sources"] = sorted(sources)
        return Response(configuration)

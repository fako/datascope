from rest_framework import generics

from datagrowth.datatypes.views import CollectionBaseContentView, CollectionBaseSerializer
from core.models.organisms import Collective, Individual


class CollectiveSerializer(CollectionBaseSerializer):

    class Meta:
        model = Collective
        fields = CollectionBaseSerializer.default_fields


class CollectiveView(generics.RetrieveAPIView):
    queryset = Collective.objects.all()
    serializer_class = CollectiveSerializer


class CollectiveContentView(CollectionBaseContentView):
    queryset = Collective.objects.all()
    content_class = Individual

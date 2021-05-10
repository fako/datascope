from rest_framework import generics

from datagrowth.datatypes.views import DocumentBaseSerializer
from core.models.organisms import Individual
from core.views.content import ContentView, ContentSerializer


class IndividualSerializer(DocumentBaseSerializer):

    class Meta:
        model = Individual
        fields = DocumentBaseSerializer.default_fields


class IndividualView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class IndividualContentView(ContentView, generics.UpdateAPIView):
    queryset = Individual.objects.all()
    serializer_class = ContentSerializer
    content_class = Individual

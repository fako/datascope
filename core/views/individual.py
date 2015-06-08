from __future__ import unicode_literals, absolute_import, print_function, division

from rest_framework import serializers, generics

from core.models.organisms import Individual
from core.views.content import ContentView, ContentSerializer


class IndividualSerializer(serializers.ModelSerializer):

    properties = serializers.SerializerMethodField()

    def get_properties(self, individual):
        return individual.properties

    class Meta:
        model = Individual
        fields = (
            "id",
            "created_at",
            "modified_at",
            "properties",
        )


class IndividualView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class IndividualContentView(ContentView, generics.UpdateAPIView):
    queryset = Individual.objects.all()
    serializer_class = ContentSerializer
    content_class = Individual


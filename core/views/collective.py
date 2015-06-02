from __future__ import unicode_literals, absolute_import, print_function, division

from django.core.exceptions import ValidationError

from rest_framework import generics, serializers, status
from rest_framework.response import Response

from core.models.organisms import Collective, Individual
from core.views.individual import IndividualSerializer
from core.views.content import ContentView, ContentSerializer, ContentPagination


class CollectiveSerializer(serializers.ModelSerializer):

    schema = serializers.SerializerMethodField()
    content = IndividualSerializer(many=True, source="individual_set")

    def get_schema(self, collective):
        return collective.schema

    class Meta:
        model = Collective
        fields = (
            "id",
            "created_at",
            "modified_at",
            "spirit",
            "schema",
            "content",
        )


class CollectiveView(generics.RetrieveAPIView):
    """
    A Collective is a list of Individuals that share the same JSON schema.
    """
    queryset = Collective.objects.all()
    serializer_class = CollectiveSerializer


class CollectiveContentView(ContentView):
    """
    A Collective is a list of Individuals that share the same JSON schema.
    """
    queryset = Collective.objects.all()
    pagination_class = ContentPagination
    content_class = Individual

    def retrieve(self, request, *args, **kwargs):
        """
        Will return a list of content which can be paginated.

        :param request: Django request
        :return: Response
        """
        # TODO: allow filtering based on GET parameters prefixed with $

        page = self.paginate_queryset(request.organism.individual_set.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(request.organism.content, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        try:
            results = self.request.organism.update(request.data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc)
        return Response([result.content for result in results], status=status.HTTP_201_CREATED)

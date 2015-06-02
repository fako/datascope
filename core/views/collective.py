from __future__ import unicode_literals, absolute_import, print_function, division

from rest_framework import generics, serializers
from rest_framework.response import Response

from core.models.organisms import Collective
from core.views.individual import IndividualSerializer

from core.views.content import ContentSerializer, ContentPagination


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


class CollectiveContentView(generics.CreateAPIView, generics.RetrieveAPIView):
    """
    A Collective is a list of Individuals that share the same JSON schema.
    """
    queryset = Collective.objects.all()
    serializer_class = ContentSerializer
    pagination_class = ContentPagination

    def dispatch(self, request, *args, **kwargs):
        request.collective = self.get_object()
        return super(CollectiveContentView, self).dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super(CollectiveContentView, self).get_serializer(*args, **kwargs)
        serializer.context["schema"] = serializer.context["request"].collective.schema
        return serializer

    def retrieve(self, request, *args, **kwargs):
        """
        Will return a list of content which can be paginated.

        :param request: Django request
        :return: Response
        """
        # TODO: allow filtering based on GET parameters prefixed with $

        page = self.paginate_queryset(request.collective.individual_set.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(request.collective.content, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        collective = self.request.collective
        data = serializer.data
        spirit = data.pop("ds_spirit", collective.spirit)
        self.request.individual = collective.individual_set.create(
            spirit=spirit,
            schema=collective.schema,
            properties=data
        )

    def create(self, request, *args, **kwargs):
        response = super(CollectiveContentView, self).create(request, *args, **kwargs)
        response.data["ds_id"] = request.individual.id
        response.data["ds_spirit"] = request.individual.spirit
        return response

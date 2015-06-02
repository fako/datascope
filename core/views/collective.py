from rest_framework import generics, serializers, pagination
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


class CollectiveContentView(generics.RetrieveAPIView):
    """
    A Collective is a list of Individuals that share the same JSON schema.
    """
    queryset = Collective.objects.all()
    serializer_class = ContentSerializer
    pagination_class = ContentPagination

    def retrieve(self, request, *args, **kwargs):
        """
        Will return a list of content which can be paginated.

        :param request: Django request
        :return: Response
        """
        # TODO: allow filtering based on GET parameters prefixed with $
        collective = self.get_object()
        context = {
            "schema": collective.schema
        }

        page = self.paginate_queryset(collective.individual_set.all())
        if page is not None:

            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(collective.content, many=True, context=context)
        return Response(serializer.data)

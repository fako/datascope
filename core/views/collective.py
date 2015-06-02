from __future__ import unicode_literals, absolute_import, print_function, division

from django.core.exceptions import ValidationError

from rest_framework import generics, serializers, status
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

    def post(self, request, *args, **kwargs):
        try:
            results = self.request.collective.update(request.data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc)
        return Response([result.content for result in results], status=status.HTTP_201_CREATED)

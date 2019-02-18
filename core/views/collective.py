from django.core.exceptions import ValidationError
from django.shortcuts import Http404

from rest_framework import generics, serializers, status
from rest_framework.response import Response

from core.models.organisms import Collective, Individual
from core.views.individual import IndividualSerializer
from core.views.content import ContentView, ContentPagination


class CollectiveSerializer(serializers.ModelSerializer):

    schema = serializers.SerializerMethodField()
    content = IndividualSerializer(many=True, source="documents")

    def get_schema(self, collective):
        return collective.schema

    class Meta:
        model = Collective
        fields = (
            "id",
            "created_at",
            "modified_at",
            "schema",
            "identifier",
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
        if request.organism is None:
            raise Http404("Not found")

        page = self.paginate_queryset(request.organism.documents.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(request.organism.content, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        # TODO: this does an add not an update. rename accordingly
        try:
            additions = self.request.organism.update(request.data, reset=False)
        except ValidationError as exc:
            schema = getattr(exc, "schema")
            return Response({"detail":
                {
                    "message": exc.message,
                    "schema": schema
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Added {} individuals".format(additions)}, status=status.HTTP_201_CREATED)

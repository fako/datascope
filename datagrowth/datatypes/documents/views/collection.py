from django.core.exceptions import ValidationError
from django.shortcuts import Http404

from rest_framework import serializers, status
from rest_framework.response import Response

from .content import ContentView, ContentPagination


class CollectionBaseSerializer(serializers.ModelSerializer):

    schema = serializers.SerializerMethodField()
    default_fields = ("id", "name", "created_at", "modified_at", "schema", "referee", "identifier", "content",)

    def get_schema(self, collective):
        return collective.schema


class CollectionBaseContentView(ContentView):
    """
    A Collection is a list of Documents that share the same JSON schema.
    """
    pagination_class = ContentPagination

    def retrieve(self, request, *args, **kwargs):
        """
        Will return a list of content which can be paginated.

        :param request: Django request
        :return: Response
        """
        if request.object is None:
            raise Http404("Not found")

        page = self.paginate_queryset(request.object.documents.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(request.object.content, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        try:
            additions = self.request.object.add(request.data)
        except ValidationError as exc:
            schema = getattr(exc, "schema")
            return Response({"detail":
                {
                    "message": exc.message,
                    "schema": schema
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Added {} documents".format(additions)}, status=status.HTTP_201_CREATED)

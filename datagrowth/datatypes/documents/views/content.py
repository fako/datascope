from django.core.exceptions import ValidationError
from django.shortcuts import Http404

from rest_framework import serializers, pagination, generics
from rest_framework.response import Response


class ContentSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if isinstance(instance, self.context["content_class"]):
            return instance.content
        elif isinstance(instance, (dict, list)):
            return instance
        else:
            assert True, "Received unexpected type {} as content.".format(type(instance))

    def to_internal_value(self, data):
        try:
            content_class = self.context["content_class"]
            data = content_class.validate(data, self.context["schema"])
        except ValidationError as exc:
            raise serializers.ValidationError(exc)
        return data

    def update(self, instance, validated_data):
        instance.update(validated_data, validate=False, reset=False)
        instance.save()
        return instance


class ContentView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer
    content_class = None

    def dispatch(self, request, *args, **kwargs):
        try:
            request.object = self.get_object()
        except Http404:
            request.object = None  # slightly suboptimal with an extra query on 404
        return super(ContentView, self).dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super(ContentView, self).get_serializer(*args, **kwargs)
        serializer.context["schema"] = serializer.context["request"].object.schema
        serializer.context["content_class"] = self.content_class
        return serializer


class ContentPagination(pagination.PageNumberPagination):

    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        if next_url is not None and previous_url is not None:
            link = '<{next_url}; rel="next">, <{previous_url}; rel="prev">'
        elif next_url is not None:
            link = '<{next_url}; rel="next">'
        elif previous_url is not None:
            link = '<{previous_url}; rel="prev">'
        else:
            link = ''

        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Link': link} if link else {}

        return Response(data, headers=headers)

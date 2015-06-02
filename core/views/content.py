from __future__ import unicode_literals, absolute_import, print_function, division

from django.core.exceptions import ValidationError

from rest_framework import serializers, pagination
from rest_framework.response import Response

from core.models.organisms import Individual


class ContentSerializer(serializers.Serializer):

    def to_representation(self, instance):
        # TODO: allow partial responses by respecting json paths after # in the URL from self.context["request"]
        if isinstance(instance, Individual):
            return instance.content
        elif isinstance(instance, dict):
            return instance
        else:
            assert True, "Received unexpected type {} as content.".format(type(instance))

    def to_internal_value(self, data):
        try:
            data = Individual.validate(data, self.context["schema"])
        except ValidationError as exc:
            raise serializers.ValidationError(exc)
        return data


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

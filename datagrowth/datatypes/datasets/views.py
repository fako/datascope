from django.core.urlresolvers import reverse

from rest_framework import serializers

from datagrowth.datatypes.datasets import DatasetState


class DatasetBaseSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()
    annotations = serializers.SerializerMethodField()

    default_fields = ("id", "signature", "created_at", "modified_at", "content", "annotations")

    def get_content(self, dataset):
        return dataset.kernel.url

    def get_annotations(self, dataset):
        if dataset.state != DatasetState.READY or not dataset.ANNOTATIONS:
            return {
                "resource": None,
                "definitions": dataset.ANNOTATIONS
            }
        return {
            "resource": reverse(
                "api-v1:{}:annotate".format(dataset.get_namespace()),
                args=(dataset.kernel.id, dataset.ANNOTATIONS[0]["name"],)
            ),
            "definitions": dataset.ANNOTATIONS
        }

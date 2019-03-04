from rest_framework import serializers


class DatasetBaseSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()
    annotations = serializers.SerializerMethodField()

    default_fields = ("id", "signature", "created_at", "modified_at", "content", "annotations")

    def get_content(self, dataset):
        return dataset.kernel.url

    def get_annotations(self, dataset):
        return dataset.ANNOTATIONS

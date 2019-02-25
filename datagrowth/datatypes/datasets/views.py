from rest_framework import serializers


class DatasetBaseSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()

    default_fields = ("id", "signature", "created_at", "modified_at", "content")

    def get_content(self, dataset):
        return dataset.kernel.url

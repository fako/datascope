from rest_framework import serializers


class DocumentBaseSerializer(serializers.ModelSerializer):

    properties = serializers.SerializerMethodField()
    default_fields = ("id", "created_at", "modified_at", "reference", "identity", "properties",)

    def get_properties(self, document):
        return document.properties

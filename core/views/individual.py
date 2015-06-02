from rest_framework import serializers

from core.models.organisms import Individual


class IndividualSerializer(serializers.ModelSerializer):

    properties = serializers.SerializerMethodField()

    def get_properties(self, individual):
        return individual.properties

    class Meta:
        model = Individual
        fields = (
            "id",
            "created_at",
            "modified_at",
            "spirit",
            "properties",
        )


class IndividualView(object):
    pass
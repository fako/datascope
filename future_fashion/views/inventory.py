from rest_framework import generics

from datagrowth.datatypes.datasets import DatasetState, DatasetBaseSerializer
from future_fashion.models import ClothingInventoryCommunity


class ClothingInventoryDatasetSerializer(DatasetBaseSerializer):

    class Meta:
        model = ClothingInventoryCommunity
        fields = DatasetBaseSerializer.default_fields


class ClothingInventoryDatasetView(generics.ListAPIView):
    """
    A view that lists details about inventory datasets
    """
    queryset = ClothingInventoryCommunity.objects.filter(state=DatasetState.READY)
    serializer_class = ClothingInventoryDatasetSerializer

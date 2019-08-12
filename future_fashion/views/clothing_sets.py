from rest_framework import generics

from future_fashion.models import ColorClothingSetSerializer


class CreateColorClothingSet(generics.CreateAPIView):
    serializer_class = ColorClothingSetSerializer

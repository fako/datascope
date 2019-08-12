from rest_framework import generics

from datagrowth.datatypes.views import (ContentView, ContentSerializer, DocumentBaseSerializer,
                                        CollectionBaseSerializer, CollectionBaseContentView)
from future_fashion.models import Collection, Document


class DocumentSerializer(DocumentBaseSerializer):

    class Meta:
        model = Document
        fields = DocumentBaseSerializer.default_fields


class DocumentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentContentView(ContentView, generics.UpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = ContentSerializer
    content_class = Document


class CollectionSerializer(CollectionBaseSerializer):

    content = DocumentSerializer(many=True, source="documents")

    class Meta:
        model = Collection
        fields = CollectionBaseSerializer.default_fields


class CollectionView(generics.RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class CollectionContentView(CollectionBaseContentView):
    queryset = Collection.objects.all()
    content_class = Document

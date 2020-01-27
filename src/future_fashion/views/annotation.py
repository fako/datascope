from datagrowth.datatypes.views import AnnotationBaseSerializer, AnnotationBaseView
from future_fashion.models import Annotation, Collection
from .data import DocumentSerializer


class AnnotationSerializer(AnnotationBaseSerializer):

    class Meta:
        model = Annotation
        fields = AnnotationBaseSerializer.default_fields


class AnnotationView(AnnotationBaseView):
    collection_model = Collection
    annotation_model = Annotation
    document_serializer = DocumentSerializer

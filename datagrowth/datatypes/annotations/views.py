from rest_framework import serializers, views, status
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from datagrowth.datatypes.views import ContentPagination


class AnnotationBaseSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()

    default_fields = ("id", "created_at", "modified_at", "username", "reference", "name", "annotation")

    def get_username(self, annotation):
        return annotation.user.username if annotation.user is not None else None


class AnnotationBaseView(views.APIView):

    collection_model = None
    annotation_model = None
    document_serializer = None

    pagination_class = ContentPagination
    annotation_page_size = 20

    def get(self, request, pk, annotation_name):
        collection = self.collection_model.objects.get(id=pk)

        previous_annotations = self.annotation_model.objects.filter(name=annotation_name)
        documents = collection.documents \
            .exclude(reference__in=previous_annotations.values("reference")) \
            .order_by("?")
        if not documents.exists():
            return Response([], status=status.HTTP_204_NO_CONTENT)

        # Get results
        serializer = self.document_serializer(documents, many=True)
        results = serializer.data[:self.annotation_page_size]

        # Enrich results with annotations
        annotations_by_reference = {result["reference"]: [] for result in results}
        for annotation in self.annotation_model.objects.filter(reference__in=annotations_by_reference.keys()).values():
            annotations_by_reference[annotation["reference"]].append(annotation)
        for result in results:
            result["annotations"] = annotations_by_reference[result["reference"]]

        return Response(results, status=status.HTTP_200_OK)

    def post(self, request, pk, annotation_name):
        # Validating
        data = request.data
        if not isinstance(data, dict):
            raise APIException("POST body should consist of an object")
        if "reference" not in data:
            raise APIException("Missing 'reference' in the POST body")
        annotations = data.get("annotations", None)
        if annotations is None:
            raise APIException("Missing 'annotations' in the POST body")
        if annotation_name not in annotations:
            raise APIException("Missing '{}' in the annotations".format(annotation_name))
        for name, value in annotations.items():
            if not isinstance(value, (str, int, float,)):
                raise APIException("{} annotation is not a string, integer or float".format(name))

        # Create or update an annotation
        user = request.user if request.user.is_authenticated else None
        for name, value in annotations.items():
            annotation, created = self.annotation_model.objects.get_or_create(
                user=user,
                reference=data["reference"],
                name=name
            )
            if isinstance(value, str):
                annotation.string = value
                annotation.value = None
            else:
                annotation.value = value
                annotation.string = None
            annotation.save()
        return Response({"detail": "Annotate success"}, status.HTTP_200_OK)

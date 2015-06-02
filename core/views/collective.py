from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveAPIView


from core.models.organisms import Collective


class CollectiveContentView(RetrieveAPIView):
    """
    A Collective is a list of Individuals that share the same JSON schema.
    """
    queryset = Collective.objects.all()

    def retrieve(self, request, *args, **kwargs):
        collective = self.get_object()
        return Response(collective.content)

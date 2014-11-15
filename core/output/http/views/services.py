from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                    HTTP_404_NOT_FOUND)

from core.exceptions import (HIFProcessingAsync, HIFProcessingError, HIFProcessingWarning, HIFBadRequest,
                             HIFNoInput)
from core.helpers.enums import ServiceTemplate, ProcessStatus as status
from core.helpers.storage import get_hif_model


class ServiceView(APIView):

    @staticmethod
    def get(request, Service):

        # Fire up the manifest
        service = Service()
        service.setup(**service.context(request))

        if service.status in service.HIF_success_statusses:
            service.views += 1
            service.save()
            return Response(data=service.content, status=HTTP_200_OK)
        else:
            return Response(data={"detail": "Service not found"}, status=HTTP_404_NOT_FOUND)

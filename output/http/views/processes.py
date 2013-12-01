from django.db.models.loading import get_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_202_ACCEPTED

from HIF.exceptions import HIFProcessingAsync, HIFProcessingError


class ProcessView(APIView):

    def get(self, request, name):

        # Sanitize GET parameters to be config parameters
        config_dict = request.GET.dict()
        if "format" in config_dict:
            del(config_dict["format"])

        # Start the process
        Process = get_model(app_label='HIF', model_name=name)
        prc = Process()
        prc.execute(**config_dict)

        # Read results
        try:
            results = prc.rsl
            return Response(data=results, status=HTTP_200_OK)
        except HIFProcessingAsync:
            return Response(data={}, status=HTTP_202_ACCEPTED)

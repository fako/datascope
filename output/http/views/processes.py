from django.db.models.loading import get_model
from django.views.generic import View
from django.shortcuts import render_to_response, RequestContext

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from HIF.exceptions import HIFProcessingAsync, HIFNoContent, HIFBadRequest, HIFNoInput
from HIF.helpers.extractors import flattener
from HIF.helpers.utils import sort_on_list_len
from HIF.helpers.enums import ServiceTemplate


class ProcessAPIView(APIView):

    def get(self, request, Service):

        # Fire up the manifest
        service = Service()

        # Prepare the process
        Process = get_model(app_label='HIF', model_name=service.HIF_process)
        prc = Process()

        # Execute and read results
        try:
            prc.execute(**service.context(request))  # could raise a 400 or HIFNoInput
            results = prc.rsl
            return Response(data=results, status=HTTP_200_OK)
        except HIFNoInput:
            return Response(data=[], status=HTTP_200_OK)
        except HIFProcessingAsync:
            return Response(data=[], status=HTTP_202_ACCEPTED)
        except HIFNoContent:
            return Response(data=[], status=HTTP_204_NO_CONTENT)
        except HIFBadRequest as exception:
            return Response(data={"detail": exception.detail}, status=HTTP_400_BAD_REQUEST)


class ProcessPlainView(View):

    def get(self, request, Service):

        # Fire up the manifest
        service = Service()
        api_response = Service.HIF_main().get(request, Service)

        if api_response.status_code == 202:
            return render_to_response(service.html_template(ServiceTemplate.ACCEPTED), {}, RequestContext(request))
        elif api_response.status_code == 204:
            return render_to_response(service.html_template(ServiceTemplate.NO_CONTENT), {}, RequestContext(request))
        elif api_response.status_code == 400:
            return render_to_response(service.html_template(ServiceTemplate.BAD_REQUEST), api_response.data, RequestContext(request))
        else:
            if api_response.data:
                return render_to_response(service.html_template(ServiceTemplate.OK), {'data': flattener(api_response.data, sort_on_list_len)},
                                  RequestContext(request))
            else:
                return render_to_response(service.html_template(ServiceTemplate.INDEX), {}, RequestContext(request))






from django.db.models.loading import get_model
from django.views.generic import View
from django.shortcuts import render_to_response, RequestContext

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from core.exceptions import HIFProcessingAsync, HIFNoContent, HIFBadRequest, HIFNoInput
from core.helpers.enums import ServiceTemplate


class ProcessAPIView(APIView):

    def get(self, request, Service):

        # Fire up the manifest
        service = Service()

        # Prepare the process
        Process = get_model(app_label='core', model_name=service.HIF_process)  # TODO: update with get_hif_model
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

        template_context = {
            'self_reverse': service.name + '-plain'
        }
        try:
            template_context.update(service.context(request))
        except (HIFNoInput, HIFBadRequest):
            pass  # No input and Bad Request have been handled by the API. We just can't get template_context here.

        if api_response.status_code == 202:
            return render_to_response(service.html_template(ServiceTemplate.ACCEPTED), template_context, RequestContext(request))
        elif api_response.status_code == 204:
            return render_to_response(service.html_template(ServiceTemplate.NO_CONTENT), template_context, RequestContext(request))
        elif api_response.status_code == 400:
            template_context.update(api_response.data)
            return render_to_response(service.html_template(ServiceTemplate.BAD_REQUEST), template_context, RequestContext(request))
        else:
            if api_response.data:
                template_context.update({'data': api_response.data })
                return render_to_response(service.html_template(ServiceTemplate.OK), template_context,
                                  RequestContext(request))
            else:
                return render_to_response(service.html_template(ServiceTemplate.INDEX), template_context, RequestContext(request))

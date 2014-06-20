from django.conf import settings

from HIF.models.settings import Domain


class AllowOriginMiddleware(object):

    @staticmethod
    def process_response(request, response):

        domain_settings = Domain()
        origin = request.META.get("HTTP_ORIGIN")
        if origin in domain_settings.HIF_allowed_origins:
            response["Access-Control-Allow-Origin"] = origin

        return response
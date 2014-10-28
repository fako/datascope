from django.conf import settings

from core.models.settings import Domain


class AllowOriginMiddleware(object):

    @staticmethod
    def process_response(request, response):

        domain_settings = Domain()
        origin = request.META.get("HTTP_ORIGIN")
        if origin in domain_settings.HIF_allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept'

        return response
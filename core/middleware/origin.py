from datascope.configuration import DEFAULT_CONFIGURATION


class AllowOriginMiddleware(object):

    @staticmethod
    def process_response(request, response):

        origin = request.META.get("HTTP_ORIGIN")
        if origin in DEFAULT_CONFIGURATION["global_allowed_origins"]:
            response["Access-Control-Allow-Origin"] = origin
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept'

        return response
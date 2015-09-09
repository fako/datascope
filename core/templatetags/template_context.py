from django.conf import settings


def core_context(request):
    return {
        "STATIC_IP": settings.STATIC_IP
    }
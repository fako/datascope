from django.conf import settings
from django.shortcuts import render_to_response, HttpResponse, Http404
from django.core.files.storage import default_storage

from visual_translations.models import VisualTranslationsEUCommunity


def visual_translation_map(request, term):
    dirs, files = default_storage.listdir('visual_translations/{}/'.format(term))
    time = request.GET.dict().get("t", None)
    if time is not None and time not in dirs:
        raise Http404("Visual translation with t={} not found or not ready".format(time))
    elif time is None:
        time = str(max((int(dir) for dir in dirs)))

    locales_info = [
        {
            "locale": "{}_{}".format(language, country),
            "small_image_file": "visual_translations/{}/{}/S_{}_{}.jpg".format(term, time, language, country),
            "large_image_file": "visual_translations/{}/{}/L_{}_{}.jpg".format(term, time, language, country),
            "xlarge_image_file": "visual_translations/{}/{}/XL_{}_{}.jpg".format(term, time, language, country),
            "grid": {
                "width": grid["cell_width"] * grid["columns"],
                "height": grid["cell_height"] * grid["rows"],
                "width_xl": grid["cell_width"] * grid["columns"] * factor,
                "height_xl": grid["cell_height"] * grid["rows"] * factor,
                "width_2": int(grid["cell_width"] * grid["columns"] / 2),
                "height_2": int(grid["cell_height"] * grid["rows"] / 2),
                "width_20": int(grid["cell_width"] * grid["columns"] / 20),
                "height_20": int(grid["cell_height"] * grid["rows"] / 20)
            }
        }
        for language, country, grid, factor in VisualTranslationsEUCommunity.LOCALES
    ]
    context = {
        "region_topo_json": "visual_translations/geo/europe.topo.json",
        "locales": locales_info,
    }
    return render_to_response("visual_translations/map.html", context, request)


def visual_translations_controller(request):
    context = {
        "words": ["pension", "peace", "women", "immigrants", "cowshed", "leave"]
    }
    return render_to_response("visual_translations/controller.html", context, request)


def web_sockets_broadcast(request, message):
    if not settings.USE_WEBSOCKETS:
        return HttpResponse('Websockets not enabled in bootstrap.py')
    try:
        from ws4redis.publisher import RedisPublisher
        from ws4redis.redis_store import RedisMessage
    except ImportError:
        return HttpResponse('Websockets package ws4redis not installed')
    redis_publisher = RedisPublisher(facility='visual-translations-map', broadcast=True)
    message = RedisMessage(message)
    redis_publisher.publish_message(message)
    return HttpResponse("Broadcast: {}".format(message))

from django.conf import settings
from django.shortcuts import render_to_response, RequestContext, HttpResponse

from visual_translations.models import VisualTranslationsEUCommunity


def visual_translation_map(request, term):
    locales_info = [
        {
            "locale": "{}_{}".format(language, country),
            "small_image_file": "visual_translations/{}/S_{}_{}.jpg".format(term, language, country),
            "large_image_file": "visual_translations/{}/L_{}_{}.jpg".format(term, language, country),
            "xlarge_image_file": "visual_translations/{}/XL_{}_{}.jpg".format(term, language, country),
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
    return render_to_response("visual_translations/map.html", context, RequestContext(request))


def visual_translations_controller(request):
    context = {
        "words": ["pension", "peace", "women", "immigrants", "cowshed", "privatization"]
    }
    return render_to_response("visual_translations/controller.html", context, RequestContext(request))


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

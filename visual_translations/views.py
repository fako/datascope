from itertools import groupby

from django.conf import settings
from django.shortcuts import render_to_response, RequestContext, HttpResponse

from core.views.community import HtmlCommunityView

from visual_translations.models import VisualTranslationsEUCommunity


class VisualTranslationsHtmlView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response):
        data = HtmlCommunityView.data_for(community_class, response)
        if response.status_code == 200:
            locale_key = lambda obj: obj["locale"]
            data["results"].sort(key=locale_key)
            response.data["results"] = [(lang, list(words),) for lang, words in groupby(data["results"], locale_key)]
            return response.data
        else:
            return response.data


def visual_translation_map(request, region, term):
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
        "region_topo_json": "visual_translations/geo/{}.topo.json".format(region),
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

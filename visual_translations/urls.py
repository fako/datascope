from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from visual_translations.models import VisualTranslationsCommunity
from visual_translations.views import (VisualTranslationsHtmlView, info, visual_translation_map,
                                       visual_translations_controller, web_sockets_broadcast)


urlpatterns = [
    url(r'^visual-translations/service/(?P<path>.+)/$', CommunityView.as_view(),
        {"community_class": VisualTranslationsCommunity}),
    url(r'^visual-translations/html/(?P<path>.+)?/?$', VisualTranslationsHtmlView.as_view(),
        {"community_class": VisualTranslationsCommunity}),
    url(r'^visual-translations/info/?$', info),
    url(r'^visual-translations/map/(?P<region>[a-z]+)/(?P<term>[a-z+]+)/?$', visual_translation_map),
    url(r'^visual-translations/controller/$', visual_translations_controller),
    url(r'^visual-translations/broadcast/(?P<message>[a-z\-]+)/?$', web_sockets_broadcast),
]
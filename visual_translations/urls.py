from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from visual_translations.models import VisualTranslationsEUCommunity
from visual_translations.views import (VisualTranslationsHtmlView, visual_translation_map,
                                       visual_translations_controller, web_sockets_broadcast)


urlpatterns = [
    url(r'^visual-translations/service/(?P<path>.+)/$', CommunityView.as_view(),
        {"community_class": VisualTranslationsEUCommunity}),
    url(r'^visual-translations/html/(?P<path>.+)?/?$', VisualTranslationsHtmlView.as_view(),
        {"community_class": VisualTranslationsEUCommunity}),
    url(r'^visual-translations-eu/map/(?P<region>[a-z]+)/(?P<term>[a-z+]+)/?$', visual_translation_map),
    url(r'^visual-translations-eu/controller/$', visual_translations_controller),
    url(r'^visual-translations-eu/broadcast/(?P<message>[a-z\-]+)/?$', web_sockets_broadcast),
]
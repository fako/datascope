from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from visual_translations.models import VisualTranslationsEUCommunity, VisualTranslationsBRICCommunity
from visual_translations.views.community import VisualTranslationsHtmlView, VisualTanslationsDisambiguationView
from visual_translations.views.eu import visual_translation_map, visual_translations_controller, web_sockets_broadcast


urlpatterns = [
    url(
        r'^visual-translations-bric/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": VisualTranslationsBRICCommunity},
        name=VisualTranslationsBRICCommunity.get_name() + "_service"
    ),
    url(
        r'^visual-translations-bric/html/(?P<path>.+)?/?$',
        VisualTranslationsHtmlView.as_view(),
        kwargs={"community_class": VisualTranslationsBRICCommunity},
        name=VisualTranslationsBRICCommunity.get_name() + "_html"
    ),

    url(
        r'^visual-translations-eu/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": VisualTranslationsEUCommunity},
        name=VisualTranslationsEUCommunity.get_name() + "_service"
    ),
    url(
        r'^visual-translations-eu/html/(?P<path>.+)?/?$',
        VisualTranslationsHtmlView.as_view(),
        kwargs={"community_class": VisualTranslationsEUCommunity},
        name=VisualTranslationsEUCommunity.get_name() + "_html"
    ),
    url(
        r'^visual-translations-eu/disambiguation/(?P<path>.+)?/?$',
        VisualTanslationsDisambiguationView.as_view(),
        kwargs={"community_class": VisualTranslationsEUCommunity},
        name=VisualTranslationsEUCommunity.get_name() + "_disambiguation"
    ),

    url(r'^visual-translations-eu/map/(?P<term>[a-z+]+)/?$', visual_translation_map),
    url(r'^visual-translations-eu/controller/$', visual_translations_controller),
    url(r'^visual-translations-eu/broadcast/(?P<message>[a-z\-]+)/?$', web_sockets_broadcast),
]
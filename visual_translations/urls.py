from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from visual_translations.models import VisualTranslationsCommunity
from visual_translations.views import VisualTranslationsHtmlView


urlpatterns = [
    url(r'^visual-translations/service/(?P<path>.+)/$', CommunityView.as_view(),
        {"community_class": VisualTranslationsCommunity}),
    url(r'^visual-translations/html/(?P<path>.+)?/?$', VisualTranslationsHtmlView.as_view(),
        {"community_class": VisualTranslationsCommunity}),
]
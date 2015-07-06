from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from visual_translations.models import VisualTranslationCommunity


urlpatterns = [
    url(r'^visual-translations/(?P<path>.+)/$', CommunityView.as_view(),
        {"community_class": VisualTranslationCommunity}),
    url(r'^visual-translations/html/(?P<path>.+)/$', HtmlCommunityView.as_view(),
        {"community_class": VisualTranslationCommunity})
]
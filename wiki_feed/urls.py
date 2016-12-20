from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from wiki_feed.models import WikiFeedCommunity
from . import views


urlpatterns = [
    url(
        r'^wiki-feed/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": WikiFeedCommunity},
        name=WikiFeedCommunity.get_name() + "_service"
    ),
    url(
        r'^wiki-feed/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": WikiFeedCommunity},
        name=WikiFeedCommunity.get_name() + "_html"
    ),
    url(r'^wiki-feed/wiki-update/(?P<page>.+)/$', views.wiki_page_update, name="wiki_page_update"),
    url(r'^wiki-feed/wiki-wait/(?P<page>.+)/$', views.wiki_page_wait, name="wiki_page_wait"),
]

from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from wiki_news.models import WikiNewsCommunity
from . import views


urlpatterns = [
    url(
        r'^wiki-algo-news/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": WikiNewsCommunity},
        name=WikiNewsCommunity.get_name() + "_service"
    ),
    url(
        r'^wiki-algo-news/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": WikiNewsCommunity},
        name=WikiNewsCommunity.get_name() + "_html"
    ),
    url(r'^wiki-algo-news/wiki-update/(?P<page>.+)/$', views.wiki_page_update, name="wiki_page_update")
]
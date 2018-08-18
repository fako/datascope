from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from wiki_scope.models import WikipediaCategorySimilarityCommunity


urlpatterns = [
    url(
        r'^category-similarity/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimilarityCommunity},
        name=WikipediaCategorySimilarityCommunity.get_name() + "_service"
    ),
    url(
        r'^category-similarity/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimilarityCommunity},
        name=WikipediaCategorySimilarityCommunity.get_name() + "_html"
    ),
]

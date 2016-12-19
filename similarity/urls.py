from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from similarity.models import WikipediaCategorySimularityCommunity


urlpatterns = [
    url(
        r'^category-similarity/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimularityCommunity},
        name=WikipediaCategorySimularityCommunity.get_name() + "_service"
    ),
    url(
        r'^category-similarity/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimularityCommunity},
        name=WikipediaCategorySimularityCommunity.get_name() + "_html"
    ),
]

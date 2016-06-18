from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from future_fashion.models import FutureFashionCommunity


urlpatterns = [
    url(
        r'^future-fashion/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": FutureFashionCommunity},
        name=FutureFashionCommunity.get_name() + "_service"
    ),
    url(
        r'^future-fashion/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": FutureFashionCommunity},
        name=FutureFashionCommunity.get_name() + "_html"
    )
]

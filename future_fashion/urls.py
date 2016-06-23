from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf.urls import url

from core.views.community import CommunityView
from future_fashion.models import FutureFashionCommunity
from future_fashion.views import FutureFashionHtmlView


urlpatterns = [
    url(
        r'^future-fashion/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": FutureFashionCommunity},
        name=FutureFashionCommunity.get_name() + "_service"
    ),
    url(
        r'^future-fashion/html/(?P<path>.+)/$',
        FutureFashionHtmlView.as_view(),
        kwargs={"community_class": FutureFashionCommunity},
        name=FutureFashionCommunity.get_name() + "_html"
    )
]

from django.conf.urls import url

from core.views.community import CommunityView
from future_fashion.models import FutureFashionCommunity
from future_fashion.views import FutureFashionHtmlView, swipe_interface_view


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
    ),
    url(
        r'^future-fashion/annotate/$',
        swipe_interface_view,
        name=FutureFashionCommunity.get_name() + "_swipe"
    )
]

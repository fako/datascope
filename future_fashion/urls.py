from django.conf.urls import url

from core.views.community import CommunityView, HtmlCommunityView
from future_fashion.models import InventoryCommunity
from future_fashion.views import swipe_interface_view


urlpatterns = [
    url(
        r'^future-fashion/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": InventoryCommunity},
        name=InventoryCommunity.get_name() + "_service"
    ),
    url(
        r'^future-fashion/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": InventoryCommunity},
        name=InventoryCommunity.get_name() + "_html"
    ),
    url(
        r'^future-fashion/annotate/$',
        swipe_interface_view,
        name=InventoryCommunity.get_name() + "_swipe"
    )
]

import os

from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

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
        name=InventoryCommunity.get_name() + "_annotate"
    )
]

mediapatterns = []
if settings.DEBUG:
    mediapatterns = static(
        settings.MEDIA_URL + "future_fashion/",
        document_root=os.path.join("future_fashion", "data", "media", "future_fashion")
    )

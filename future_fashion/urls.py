import os

from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from core.views.community import CommunityView, HtmlCommunityView
from future_fashion.models import ClothingInventoryCommunity
from future_fashion.views import swipe_interface_view, CreateColorClothingSet


urlpatterns = [
    url(
        r'^future-fashion/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": ClothingInventoryCommunity},
        name=ClothingInventoryCommunity.get_name() + "_service"
    ),
    url(
        r'^future-fashion/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": ClothingInventoryCommunity},
        name=ClothingInventoryCommunity.get_name() + "_html"
    ),
    url(
        r'^future-fashion/annotate/$',
        swipe_interface_view,
        name=ClothingInventoryCommunity.get_name() + "_annotate"
    ),
    url(
        r'^future-fashion/color-clothing-set/$',
        CreateColorClothingSet.as_view(),
        name="color_clothing_set"
    )
]

mediapatterns = []
if settings.DEBUG:
    mediapatterns = static(
        settings.MEDIA_URL + "future_fashion/",
        document_root=os.path.join("future_fashion", "data", "media", "future_fashion")
    )

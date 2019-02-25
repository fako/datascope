from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from datagrowth.utils import get_media_path
from core.views.community import CommunityView, HtmlCommunityView
from future_fashion.models import ClothingInventoryCommunity
from future_fashion import views


urlpatterns = [
    url(
        r'^inventory/service/(?P<path>.+)/?$',
        CommunityView.as_view(),
        kwargs={"community_class": ClothingInventoryCommunity},
        name=ClothingInventoryCommunity.get_name() + "_service"
    ),
    url(
        r'^inventory/html/(?P<path>.+)/?$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": ClothingInventoryCommunity},
        name=ClothingInventoryCommunity.get_name() + "_html"
    ),
    url(
        r'^inventory/datasets/?$',
        views.ClothingInventoryDatasetView.as_view(),
        name=ClothingInventoryCommunity.get_name() + "_datasets"
    ),
    url(
        r'^paper-doll/?$',
        views.swipe_interface_view,
        name=ClothingInventoryCommunity.get_name() + "_paper_doll"
    ),
    url(
        r'^color-clothing-set/?$',
        views.CreateColorClothingSet.as_view(),
        name="color_clothing_set"
    ),
    url(r'^data/collection/(?P<pk>\d+)/content/?$', views.CollectionContentView.as_view(), name="collection-content"),
    url(r'^data/collection/(?P<pk>\d+)/?$', views.CollectionView.as_view(), name="collection"),
    url(r'^data/document/(?P<pk>\d+)/content/?$', views.DocumentContentView.as_view(), name="document-content"),
    url(r'^data/document/(?P<pk>\d+)/?$', views.DocumentView.as_view(), name="document"),
]

mediapatterns = []
if settings.DEBUG:
    mediapatterns = static(
        settings.MEDIA_URL + "future_fashion/",
        document_root=get_media_path("future_fashion")
    )

from django.urls import re_path
from rest_framework import routers

from core.views.community import CommunityView
from online_discourse.models import DiscourseSearchCommunity
from online_discourse import views


app_name = "online-discourse"
urlpatterns = [
    re_path(
        r'^service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_service"
    ),
    re_path(
        r'^search/(?P<path>.+)/$',
        views.DiscourseSearchView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_search"
    ),
    re_path(
        r'^order/?$',
        views.CreateDiscourseOrder.as_view(),
        name=DiscourseSearchCommunity.get_name() + "_order"
    ),
    re_path(r'^data/collection/(?P<pk>\d+)/content/?$', views.CollectionContentView.as_view(), name="collection-content"),
    re_path(r'^data/collection/(?P<pk>\d+)/?$', views.CollectionView.as_view(), name="collection"),
    re_path(r'^data/document/(?P<pk>\d+)/content/?$', views.DocumentContentView.as_view(), name="document-content"),
    re_path(r'^data/document/(?P<pk>\d+)/?$', views.DocumentView.as_view(), name="document"),
]


router = routers.SimpleRouter()
router.register(
    'discourses',
    views.DiscourseViewSet,
    basename=DiscourseSearchCommunity.get_name()
)
urlpatterns += router.urls

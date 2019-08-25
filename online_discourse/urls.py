from django.conf.urls import url
from rest_framework import routers

from core.views.community import CommunityView
from online_discourse.models import DiscourseSearchCommunity
from online_discourse import views


urlpatterns = [
    url(
        r'^service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": DiscourseSearchCommunity},
        name=DiscourseSearchCommunity.get_name() + "_service"
    ),
    url(
        r'^order/?$',
        views.CreateDiscourseOrder.as_view(),
        name=DiscourseSearchCommunity.get_name() + "_order"
    ),
    url(r'^data/collection/(?P<pk>\d+)/content/?$', views.CollectionContentView.as_view(), name="collection-content"),
    url(r'^data/collection/(?P<pk>\d+)/?$', views.CollectionView.as_view(), name="collection"),
    url(r'^data/document/(?P<pk>\d+)/content/?$', views.DocumentContentView.as_view(), name="document-content"),
    url(r'^data/document/(?P<pk>\d+)/?$', views.DocumentView.as_view(), name="document"),
]


router = routers.SimpleRouter()
router.register(
    'discourses',
    views.DiscourseViewSet,
    base_name=DiscourseSearchCommunity.get_name()
)
urlpatterns += router.urls

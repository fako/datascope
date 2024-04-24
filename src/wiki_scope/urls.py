from django.urls import re_path

from core.views.community import CommunityView, HtmlCommunityView
from wiki_scope.models import WikipediaCategorySimilarityCommunity


app_name = "wiki_scope"
urlpatterns = [
    re_path(
        r'^category-similarity/service/(?P<path>.+)/$',
        CommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimilarityCommunity},
        name=WikipediaCategorySimilarityCommunity.get_name() + "_service"
    ),
    re_path(
        r'^category-similarity/html/(?P<path>.+)/$',
        HtmlCommunityView.as_view(),
        kwargs={"community_class": WikipediaCategorySimilarityCommunity},
        name=WikipediaCategorySimilarityCommunity.get_name() + "_html"
    ),
]

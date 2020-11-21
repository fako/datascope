from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views import static

from rest_framework.authtoken import views as rest_views

from datascope import views
from core import views as core_views
from wiki_feed.urls import urlpatterns as wiki_feed_patterns
from visual_translations.urls import urlpatterns as visual_translations_patterns
from future_fashion import urls as future_fashion_urls
from future_fashion.urls import mediapatterns
from wiki_scope.urls import urlpatterns as wiki_scope_patterns
from online_discourse import urls as online_discourse_urls


admin.autodiscover()


#############################################
# LEGACY PATTERNS PREFIXED WITH /data/
#############################################

legacy_patterns = [
    url(r'^collective/(?P<pk>\d+)/content/$', core_views.CollectiveContentView.as_view(), name="collective-content"),
    url(r'^collective/(?P<pk>\d+)/$', core_views.CollectiveView.as_view(), name="collective"),
    url(r'^individual/(?P<pk>\d+)/content/$', core_views.IndividualContentView.as_view(), name="individual-content"),
    url(r'^individual/(?P<pk>\d+)/$', core_views.IndividualView.as_view(), name="individual"),
    url(r'^question/$', views.question, name="datascope-question")
]
legacy_patterns += wiki_feed_patterns
legacy_patterns += visual_translations_patterns
legacy_patterns += wiki_scope_patterns
if settings.USE_MOCKS:
    from core.tests.mocks.urls import urlpatterns as mock_patterns
    legacy_patterns += mock_patterns


#############################################
# DATAGROWTH PATTERNS PREFIXED WITH /api/
#############################################

datagrowth_patterns = [
    url(r'^future-fashion/', include(future_fashion_urls)),
    url(r'^discourse-search/', include(online_discourse_urls)),
]


#############################################
# PRODUCTION PATTERNS
#############################################

urlpatterns = [
    url(r'^$', views.index, name="datascope-index"),
    url(r'^data/v1/', include((legacy_patterns, "v1",))),
    url(r'^api/v1/auth/token/?$', rest_views.obtain_auth_token),
    url(r'^api/v1/', include((datagrowth_patterns, "api-v1",))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^health/?$', views.health_check),
]


#############################################
# DEVELOPMENT PATTERNS
#############################################

if settings.DEBUG:
    urlpatterns += mediapatterns
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', static.serve,
            {'document_root': settings.STATIC_ROOT })
    ]
if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

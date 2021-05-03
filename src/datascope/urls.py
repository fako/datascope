from django.conf.urls import include, url
from django.urls import path, re_path
from django.conf import settings
from django.contrib import admin
from django.views import static
from django.conf.urls.i18n import i18n_patterns

from rest_framework.authtoken import views as rest_views

from datascope import views
from core import urls as core_patterns
from apps.views import webapp
from visual_translations import urls as visual_translations_patterns
from future_fashion import urls as future_fashion_urls
from future_fashion.urls import mediapatterns
from wiki_scope import urls as wiki_scope_patterns
from online_discourse import urls as online_discourse_urls


admin.autodiscover()


#############################################
# DATAGROWTH PATTERNS PREFIXED WITH /api/
#############################################

datagrowth_patterns = [
    url(r'^future-fashion/', include(future_fashion_urls)),
    url(r'^discourse-search/', include(online_discourse_urls)),
    # TODO: use stricter URLs with more prefixes here
    url(r'', include(visual_translations_patterns)),
    url(r'', include(core_patterns)),
    url(r'', include(wiki_scope_patterns)),

    url(r'^question/$', views.question, name="datascope-question")
]


#############################################
# PRODUCTION PATTERNS
#############################################

urlpatterns = [
    url(r'^api/v1/?$', views.index, name="datascope-index"),
    url(r'^api/v1/auth/token/?$', rest_views.obtain_auth_token),
    url(r'^api/v1/', include((datagrowth_patterns, "v1",))),
    url(r'^admin/', admin.site.urls),
    url(r'^health/?$', views.health_check),
    path("discourse-scope-promo/", webapp, {"path": ""}, name='discourse-scope-promo'),
    re_path('^discourse-scope/?(?P<path>.*)?', webapp, name='discourse-scope'),
    re_path("globe-scope/?(?P<path>.*)?", webapp, {"path": ""}, name='globe-scope'),
]

urlpatterns += i18n_patterns(
    path("", webapp, {"path": ""}, name='root'),
    path("gff/", webapp, {"path": ""}, name='gff'),
)


#############################################
# DEVELOPMENT PATTERNS
#############################################

if settings.DEBUG:
    urlpatterns += mediapatterns
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        url(r'^static/(?P<path>.*)$', static.serve,
            {'document_root': settings.STATIC_ROOT})
    ]
if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

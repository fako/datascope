from django.conf.urls import include
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
from wiki_scope import urls as wiki_scope_patterns
from online_discourse import urls as online_discourse_urls


admin.autodiscover()


#############################################
# DATAGROWTH PATTERNS PREFIXED WITH /api/
#############################################

datagrowth_patterns = [
    re_path(r'^discourse-search/', include(online_discourse_urls)),
    # TODO: use stricter URLs with more prefixes here
    re_path(r'', include(core_patterns)),
    re_path(r'', include(wiki_scope_patterns)),
    re_path(r'', include(visual_translations_patterns)),
    re_path(r'^question/$', views.question, name="datascope-question")
]


#############################################
# PRODUCTION PATTERNS
#############################################

urlpatterns = [
    re_path(r'^api/v1/?$', views.index, name="datascope-index"),
    re_path(r'^api/v1/auth/token/?$', rest_views.obtain_auth_token),
    re_path(r'^api/v1/', include((datagrowth_patterns, "v1",))),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^health/?$', views.health_check),
    path("ai-brainstorm/", webapp, {"path": ""}, name='ai-brainstorm'),
    path("about/", webapp, {"path": ""}, name='datascope-about'),
    path("discourse-scope-promo/", webapp, {"path": ""}, name='discourse-scope-promo'),
    re_path('^discourse-scope/?(?P<path>.*)?', webapp, name='discourse-scope'),
    re_path("globe-scope/?(?P<path>.*)?", webapp, {"path": ""}, name='globe-scope'),
]

urlpatterns += i18n_patterns(
    path("", webapp, {"path": ""}, name='root'),
)


#############################################
# DEVELOPMENT PATTERNS
#############################################

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
        re_path(r'^static/(?P<path>.*)$', static.serve,
            {'document_root': settings.STATIC_ROOT})
    ]
if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

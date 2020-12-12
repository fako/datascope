from django.shortcuts import render, Http404
from django.templatetags.static import static
from django.template.exceptions import TemplateDoesNotExist


from apps.models import Webapp


def webapp(request, path):

    route = request.resolver_match.url_name
    current_language = request.LANGUAGE_CODE.split("-")[0]
    base = request.path_info.replace(path, "")

    current_app = None
    language_links = []
    for app in Webapp.objects.filter(route=route).select_related("site"):
        if app.language == current_language:
            current_app = app
        language_links.append(
            (app.locale, app.build_absolute_uri(),)
        )

    if not current_app:
        raise Http404('Could not find "{}" app for language "{}"'.format(route, current_language))

    context = {
        "BUNDLE": "{}-{}".format(current_app.package.upper(), current_app.version),
        "APP_BASE": base,
        "STATICS_PREFIX": static(current_app.statics_prefix),
        "domain": current_app.site.domain,
        "app": current_app,
        "language_links": language_links
    }
    try:
        response = render(request, "apps/{}.html".format(current_app.package), context=context)
    except TemplateDoesNotExist:
        raise Http404('Could not find template for app "{}"'.format(current_app.package))
    return response

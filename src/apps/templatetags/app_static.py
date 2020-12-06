import os

from django import template
from django.templatetags.static import static


register = template.Library()


@register.simple_tag
def app_static(app, file_path):
    return static(os.path.join(app.statics_prefix, file_path))
